from collections.abc import Mapping

from gyomu_schema.error.base import BaseError, caller_context


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
