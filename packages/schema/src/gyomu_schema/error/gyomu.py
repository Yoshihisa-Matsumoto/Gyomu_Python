
from collections.abc import Mapping
from typing import Literal

from gyomu_schema.error.base import BaseError

GyomuErrorReason = Literal[
    "invalid_input",
    "not_found",
    "external_failure",
    "unexpected",
    "concurrent_modification",
    "out_of_bounds",
]



class GyomuError(BaseError):
    """Application-level Gyomu error."""

    def __init__(
        self,
        message: str,
        *,
        operation: str,
        domain: str,
        reason: GyomuErrorReason,
        retryable: bool = False,
        context: str | None = None,
        details: Mapping[str, object] | None = None,
    ) -> None:
        super().__init__(
            message,
            context=context,
            details=details,
        )
        self.operation = operation
        self.domain = domain
        self.reason = reason
        self.retryable = retryable
