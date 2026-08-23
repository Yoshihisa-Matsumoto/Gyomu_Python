from collections.abc import Mapping

from gyomu_schema.error.base import BaseError


class ValidationError(BaseError):
    """Validation error."""

    def __init__(
        self,
        message: str,
        *,
        location: tuple[str | int, ...] | None = None,
        input: object | None = None,
        context: str | None = None,
        details: Mapping[str, object] | None = None,
    ) -> None:
        super().__init__(
            message,
            context=context,
            details=details,
        )
        self.location = location
        self.input = input
