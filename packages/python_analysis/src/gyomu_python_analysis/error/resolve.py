from collections.abc import Mapping
from pathlib import Path

from gyomu_schema.error.base import BaseError, caller_context


class ResolveError(BaseError):
    def __init__(
        self,
        message: str,
        *,
        reference: str | Path,
        details: Mapping[str, object] | None = None,
    ) -> None:
        super().__init__(
            message,
            context=caller_context(),
            details=details,
        )
        self.reference = reference
