from collections.abc import Mapping

from gyomu_schema.error.base import BaseError


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
