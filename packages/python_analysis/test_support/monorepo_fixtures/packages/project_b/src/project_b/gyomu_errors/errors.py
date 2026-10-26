from collections.abc import Mapping

from gyomu_schema.error.base import caller_context
from project_a.gyomu_errors.base import BasedError


class NonTargetError(Exception):

    def __init__(
        self,
        message: str,
    ) -> None:
        super().__init__(
            message,
        )

class InheritError(BasedError):
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
