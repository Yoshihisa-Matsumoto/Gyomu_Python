from collections.abc import Mapping

from gyomu_schema.error.base import BaseError


class ProcessError(BaseError):
    """Subprocess error."""

    def __init__(
        self,
        message: str,
        *,
        command: tuple[str, ...],
        exit_code: int | None,
        context: str | None = None,
        details: Mapping[str, object] | None = None,
    ) -> None:
        super().__init__(
            message,
            context=context,
            details=details,
        )
        self.command = command
        self.exit_code = exit_code
