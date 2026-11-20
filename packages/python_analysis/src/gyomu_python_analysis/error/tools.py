from collections.abc import Mapping

from gyomu_schema.error.base import BaseError, caller_context


class ToolConfigError(BaseError):
    def __init__(
        self,
        message: str,
        details: Mapping[str, object] | None = None,
    ) -> None:
        super().__init__(
            message,
            context=caller_context(),
            details=details,
        )


class MypyCheckExecutionError(BaseError):
    command: list[str]
    env: dict[str, str] | None

    def __init__(
        self,
        message: str,
        command: list[str],
        env: dict[str, str] | None,
        details: Mapping[str, object] | None = None,
    ) -> None:
        super().__init__(
            message,
            context=caller_context(),
            details=details,
        )
        self.command = command
        self.env = env
