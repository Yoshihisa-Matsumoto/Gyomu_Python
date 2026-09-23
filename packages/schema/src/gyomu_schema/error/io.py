from collections.abc import Mapping
from enum import StrEnum

from gyomu_schema.error.base import BaseError


class IOLayer(StrEnum):
    STREAM = "stream"
    FILESYSTEM = "filesystem"
    CSV = "csv"
    ARCHIVE = "archive"


class IOOperation(StrEnum):
    READ = "read"
    WRITE = "write"
    OPEN = "open"
    CLOSE = "close"
    TRANSFORM = "transform"
    DELETE = "delete"


class GyomuIOError(BaseError):
    """I/O operation error."""

    def __init__(
        self,
        message: str,
        *,
        layer: IOLayer,
        operation: IOOperation,
        target: str | None = None,
        retryable: bool = False,
        reason: str | None = None,
        context: str | None = None,
        details: Mapping[str, object] | None = None,
    ) -> None:
        super().__init__(
            message,
            context=context,
            details=details,
        )
        self.layer = layer
        self.operation = operation
        self.target = target
        self.retryable = retryable
        self.reason = reason
