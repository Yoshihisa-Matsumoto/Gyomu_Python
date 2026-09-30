from collections.abc import Mapping

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


class PyProjectStructureValidationError(BaseError):
    """Raised when a pyproject structure validation error occurs.

    Raised when the pyproject structure validation fails.
    """

    def __init__(
        self,
        message: str,
        *,
        path: ProjectRelativePath,
        context: str | None = None,
        details: Mapping[str, object] | None = None,
    ) -> None:
        super().__init__(
            message,
            context=context,
            details=details,
        )
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
