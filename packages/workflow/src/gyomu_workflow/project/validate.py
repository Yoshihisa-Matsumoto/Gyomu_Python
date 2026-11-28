from pathlib import Path

from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.schemas.python.types import ProjectRelativePath
from returns.result import Failure, Result, Success

from gyomu_workflow.project.error import (
    PyProjectStructureErrorKind,
    PyProjectStructureValidationError,
    PyProjectStructureValidationErrors,
)
from gyomu_workflow.project.repair import repair_python_package_structure


def validate_python_package_structure(
    project_context: ProjectContext,
) -> Result[None, PyProjectStructureValidationErrors]:
    """Validate Python package structure.

    Validates the Python package structure within a project context, ensuring required
    __init__.py files are present.

    Args:
        project_context (ProjectContext): The project context containing source root and
            project root paths.

    Returns:
        Result[None, PyProjectStructureValidationErrors]: Success with None if the
            package structure is valid, or Failure with
            PyProjectStructureValidationErrors otherwise.
    """
    source_root_full_path = project_context.project_root / project_context.source_root
    errors: list[PyProjectStructureValidationError] = []

    def validate_directory(path: Path) -> bool:
        entries = tuple(path.iterdir())

        has_python_file = any(
            entry.is_file() and entry.suffix == ".py" for entry in entries
        )

        has_python_file_in_children = False

        for entry in entries:
            if entry.is_dir() and validate_directory(entry):
                has_python_file_in_children = True

        contains_python_file = has_python_file or has_python_file_in_children

        if contains_python_file and not (path / "__init__.py").is_file():
            errors.append(
                PyProjectStructureValidationError(
                    "__init__.py does not exist",
                    kind=PyProjectStructureErrorKind.MISSING_INIT_FILE,
                    path=ProjectRelativePath(
                        path.relative_to(project_context.project_root)
                    ),
                )
            )

        return contains_python_file

    for entry in source_root_full_path.iterdir():
        if entry.is_dir():
            validate_directory(entry)

    # test_root_full_path = project_context.project_root / project_context.test_root
    # for entry in test_root_full_path.iterdir():
    #     if entry.is_dir():
    #         validate_directory(entry)

    for package_root in project_context.package_roots:
        package_root_full_path = project_context.project_root / package_root.path

        if not (package_root_full_path / "py.typed").is_file():
            errors.append(
                PyProjectStructureValidationError(
                    "py.typed does not exist",
                    kind=PyProjectStructureErrorKind.MISSING_PY_TYPED_FILE,
                    path=package_root.path,
                )
            )

    if errors:
        return Failure(
            PyProjectStructureValidationErrors(
                message="Invalid structure on project",
                errors=tuple(errors),
                project_name=project_context.config.name,
            )
        )

    return Success(None)


def validate_and_fix_python_package_structure(
    project_context: ProjectContext,
) -> Result[None, GyomuError]:
    validation_result = validate_python_package_structure(project_context)

    if isinstance(validation_result, Failure):
        repair_result = repair_python_package_structure(
            project_context=project_context, errors=validation_result.failure().errors
        )
        if isinstance(repair_result, Failure):
            return repair_result.alt(
                lambda error: GyomuError(
                    message="fail to validate project structure",
                    domain="snapshot",
                    operation="resolve_snapshot_target",
                    reason="external_failure",
                ).chain(error)
            )
        validation_result = validate_python_package_structure(project_context)

    return validation_result.alt(
        lambda error: GyomuError(
            message="fail to repair project structure",
            domain="snapshot",
            operation="resolve_snapshot_target",
            reason="external_failure",
        ).chain(error)
    )
