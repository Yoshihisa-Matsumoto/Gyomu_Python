from collections.abc import Mapping

from gyomu_schema.error.base import BaseError, caller_context


class GyomuTestError(BaseError):
    """General error in gyomu-test."""

    def __init__(
        self,
        message: str,
        *,
        details: Mapping[str, object] | None = None,
    ) -> None:
        super().__init__(
            message,
            context=caller_context(),
            details=details,
        )
