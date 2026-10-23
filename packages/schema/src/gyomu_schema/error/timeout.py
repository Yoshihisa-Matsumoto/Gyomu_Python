from collections.abc import Mapping

from gyomu_schema.error.base import BaseError, caller_context


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
        if context is None:
            context = caller_context()
        super().__init__(
            message,
            context=context,
            details=details,
        )
        self.action = action
        self.timeout_seconds = timeout_seconds
        self.interval_seconds = interval_seconds
        self.elapsed_seconds = elapsed_seconds
