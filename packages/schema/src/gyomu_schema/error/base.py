from collections.abc import Mapping


class BaseError(Exception):
    """Base class for Gyomu errors."""

    def __init__(
        self,
        message: str,
        *,
        context: str | None = None,
        details: Mapping[str, object] | None = None,
    ) -> None:
        super().__init__(message)
        self.context = context
        self.details = details
