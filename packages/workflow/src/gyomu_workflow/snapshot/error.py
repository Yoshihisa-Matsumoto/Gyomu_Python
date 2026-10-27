from collections.abc import Mapping
from enum import StrEnum

from gyomu_schema.error.base import BaseError, caller_context
from gyomu_schema.schemas.python.types import ProjectRelativePath


class SnapshotRequestValidationError(BaseError):
    """SnapshotRequest validation error."""

    code: str
    field: str | None
    expected: object | None
    actual: object | None

    def __init__(
        self,
        message: str,
        *,
        code: str,
        field: str | None = None,
        expected: object | None = None,
        actual: object | None = None,
        details: Mapping[str, object] | None = None,
    ) -> None:
        super().__init__(
            message,
            context=caller_context(),
            details=details,
        )
        self.code = code
        self.field = field
        self.expected = expected
        self.actual = actual


class PyProjectStructureErrorKind(StrEnum):
    """PyProject structure error kind.

    PyProject structure error kind.
    """

    MISSING_INIT_FILE = "missing_init_file"
    """Missing `__init__.py` file error.

    Missing `__init__.py` file error.
    """
    MISSING_PY_TYPED_FILE = "missing_py_typed_file"
    """Missing `py.typed` file error.

    Missing `py.typed` file error.
    """


class PyProjectStructureValidationError(BaseError):
    """Raised when a pyproject structure validation error occurs.

    Raised when the pyproject structure validation fails.
    """

    kind: PyProjectStructureErrorKind
    path: ProjectRelativePath

    def __init__(
        self,
        message: str,
        *,
        kind: PyProjectStructureErrorKind,
        path: ProjectRelativePath,
        details: Mapping[str, object] | None = None,
    ) -> None:
        super().__init__(
            message,
            context=caller_context(),
            details=details,
        )
        self.kind = kind
        self.path = path


class PyProjectStructureValidationErrors(BaseError):
    """Raised when multiple pyproject structure validation errors occur."""

    project_name: str
    errors: tuple[PyProjectStructureValidationError, ...]

    def __init__(
        self,
        message: str,
        *,
        project_name: str,
        errors: tuple[PyProjectStructureValidationError, ...],
        details: Mapping[str, object] | None = None,
    ) -> None:
        super().__init__(
            message,
            context=caller_context(),
            details=details,
        )
        self.project_name = project_name
        self.errors = errors
