from collections.abc import Mapping

from gyomu_schema.error.base import BaseError, caller_context


class ProcessError(BaseError):
    """Subprocess error."""

    command: tuple[str, ...]
    exit_code: int | None

    def __init__(
        self,
        message: str,
        *,
        command: tuple[str, ...],
        exit_code: int | None,
        details: Mapping[str, object] | None = None,
    ) -> None:
        context = caller_context()
        super().__init__(
            message,
            context=context,
            details=details,
        )
        self.command = command
        self.exit_code = exit_code
