from collections.abc import Mapping
from enum import StrEnum

from gyomu_schema.error.base import BaseError


class IOLayer(StrEnum):
    """Enumeration of I/O layers."""

    STREAM = "stream"
    """Stream I/O layer."""

    FILESYSTEM = "filesystem"
    """Filesystem I/O layer."""

    CSV = "csv"
    """CSV I/O layer."""

    ARCHIVE = "archive"
    """Archive I/O layer."""


class IOOperation(StrEnum):
    """Enumeration of I/O operations."""

    READ = "read"
    """Read operation."""

    WRITE = "write"
    """Write operation."""

    OPEN = "open"
    """Open operation."""

    CLOSE = "close"
    """Close operation."""

    TRANSFORM = "transform"
    """Transform operation."""

    DELETE = "delete"
    """Delete operation."""


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
