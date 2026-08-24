from collections.abc import Mapping

from gyomu_schema.error.base import BaseError


class GyomuTimeoutError(BaseError):
    """Timeout related error."""

    def __init__(
        self,
        message: str,
        *,
        action: str,
        timeout_seconds: float,
        interval_seconds: float | None = None,
        elapsed_seconds: float | None = None,
        context: str | None = None,
        details: Mapping[str, object] | None = None,
    ) -> None:
        super().__init__(
            message,
            context=context,
            details=details,
        )
        self.action = action
        self.timeout_seconds = timeout_seconds
        self.interval_seconds = interval_seconds
        self.elapsed_seconds = elapsed_seconds
