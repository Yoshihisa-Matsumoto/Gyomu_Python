from collections.abc import Mapping
from enum import StrEnum

from gyomu_schema.error.base import BaseError
from gyomu_schema.schemas.python.types import ProjectRelativePath


class SnapshotRequestValidationError(BaseError):
    """SnapshotRequest validation error."""

    def __init__(
        self,
        message: str,
        *,
        code: str,
        field: str | None = None,
        expected: object | None = None,
        actual: object | None = None,
        context: str | None = None,
        details: Mapping[str, object] | None = None,
    ) -> None:
        super().__init__(
            message,
            context=context,
            details=details,
        )
        self.code = code
        self.field = field
        self.expected = expected
        self.actual = actual


class PyProjectStructureErrorKind(StrEnum):
    MISSING_INIT_FILE = "missing_init_file"
    MISSING_PY_TYPED_FILE = "missing_py_typed_file"


class PyProjectStructureValidationError(BaseError):
    """Raised when a pyproject structure validation error occurs.

    Raised when the pyproject structure validation fails.
    """

    def __init__(
        self,
        message: str,
        *,
        kind: PyProjectStructureErrorKind,
        path: ProjectRelativePath,
        context: str | None = None,
        details: Mapping[str, object] | None = None,
    ) -> None:
        super().__init__(
            message,
            context=context,
            details=details,
        )
        self.kind = kind
        self.path = path


class PyProjectStructureValidationErrors(BaseError):
    """Raised when multiple pyproject structure validation errors occur."""

    def __init__(
        self,
        message: str,
        *,
        project_name: str,
        errors: tuple[PyProjectStructureValidationError, ...],
        context: str | None = None,
        details: Mapping[str, object] | None = None,
    ) -> None:
        super().__init__(
            message,
            context=context,
            details=details,
        )
        self.project_name = project_name
        self.errors = errors
