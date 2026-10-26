
from typing import Mapping

from gyomu_schema.error.base import BaseError, caller_context


class BasedError(BaseError):

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
