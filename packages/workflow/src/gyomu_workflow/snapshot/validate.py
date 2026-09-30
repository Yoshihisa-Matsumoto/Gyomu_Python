from pathlib import Path

from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.schemas.python.types import ProjectRelativePath
from returns.result import Failure, Result, Success

from gyomu_workflow.snapshot.error import (
    PyProjectStructureValidationError,
    PyProjectStructureValidationErrors,
    SnapshotRequestValidationError,
)
from gyomu_workflow.snapshot.models import SnapshotRequest


def validate_snapshot_request(
    request: SnapshotRequest,
) -> Result[None, SnapshotRequestValidationError]:
    """Validate a snapshot request.

    Validates a snapshot request against validation rules.

    Args:
        request (SnapshotRequest): The snapshot request to validate.

    Returns:
        Result[None, SnapshotRequestValidationError]: Success with None if valid, or
            Failure with SnapshotRequestValidationError if invalid.
    """
    if request.option.target.all and not request.option.commit:
        return Failure(
            SnapshotRequestValidationError(
                code="commit_required_for_all",
                message="commit must be enabled when all is true.",
                field="option.commit",
                expected=True,
                actual=False,
            )
        )
    return Success(None)


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
                    path=ProjectRelativePath(
                        path.relative_to(project_context.project_root)
                    ),
                )
            )

        return contains_python_file

    for entry in source_root_full_path.iterdir():
        if entry.is_dir():
            validate_directory(entry)

    for package_root in project_context.package_roots:
        package_root_full_path = project_context.project_root / package_root

        if not (package_root_full_path / "py.typed").is_file():
            errors.append(
                PyProjectStructureValidationError(
                    "py.typed does not exist",
                    path=package_root,
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
