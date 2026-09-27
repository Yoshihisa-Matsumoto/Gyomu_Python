from pathlib import Path

from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.schemas.python.types import ProjectRelativePath
from returns.result import Failure, Result, Success

from gyomu_workflow.snapshot.error import (
    PyProjectStructureValidationError,
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
) -> Result[None, PyProjectStructureValidationError]:
    """Validate Python package structure.

    Validates the Python package structure within a project context, ensuring required
    __init__.py files are present.

    Args:
        project_context (ProjectContext): The project context containing source root and
            project root paths.

    Returns:
        Result[None, PyProjectStructureValidationError]: Success with None if the
            package structure is valid, or Failure with
            PyProjectStructureValidationError otherwise.
    """
    source_root_full_path = project_context.project_root / project_context.source_root

    def validate_directory(
        path: Path,
    ) -> Result[None, PyProjectStructureValidationError]:
        entries = tuple(path.iterdir())

        has_python_file = any(
            entry.is_file() and entry.suffix == ".py" for entry in entries
        )

        if has_python_file and not (path / "__init__.py").is_file():
            return Failure(
                PyProjectStructureValidationError(
                    "__init__.py does not exist",
                    path=ProjectRelativePath(
                        path.relative_to(project_context.project_root)
                    ),
                )
            )

        for entry in entries:
            if entry.is_dir():
                result = validate_directory(entry)
                if isinstance(result, Failure):
                    return result

        return Success(None)

    return validate_directory(source_root_full_path)
