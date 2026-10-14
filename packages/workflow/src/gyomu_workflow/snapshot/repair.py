from gyomu_infra.filesystem.file_io import write_text
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.error.io import GyomuIOError
from gyomu_schema.schemas.types import FullPath
from returns.result import Failure, Result, Success

from gyomu_workflow.snapshot.error import (
    PyProjectStructureErrorKind,
    PyProjectStructureValidationError,
)


def create_file_if_not_exist(path: FullPath) -> Result[None, GyomuIOError]:
    """Create a file with empty content if it does not already exist.

    Args:
        path (FullPath): Path to the file to create.

    Returns:
        Result[None, GyomuIOError]: A Result containing None on success or a
            GyomuIOError on failure.
    """
    if not path.exists():
        return write_text(path=path, content="")
    return Success(None)


def repair_python_package_structure(
    project_context: ProjectContext,
    errors: tuple[PyProjectStructureValidationError, ...],
) -> Result[None, GyomuIOError]:
    """Repair Python package structure validation errors by creating missing init or
    py.typed files.

    Args:
        project_context (ProjectContext): The project context containing the project
            root.
        errors (tuple[PyProjectStructureValidationError, ...]): A tuple of structure
            validation errors to repair.

    Returns:
        Result[None, GyomuIOError]: A Result containing None on success or a
            GyomuIOError on failure.
    """
    for error in errors:
        if error.kind == PyProjectStructureErrorKind.MISSING_INIT_FILE:
            init_path = project_context.project_root / error.path / "__init__.py"
            init_result = create_file_if_not_exist(init_path)
            if isinstance(init_result, Failure):
                return init_result
        elif error.kind == PyProjectStructureErrorKind.MISSING_PY_TYPED_FILE:
            pytyped_path = project_context.project_root / error.path / "py.typed"
            pytyped_result = create_file_if_not_exist(pytyped_path)
            if isinstance(pytyped_result, Failure):
                return pytyped_result

    return Success(None)
