from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum

from gyomu_schema.error.base import BaseError


class AiOperation(StrEnum):
    """Defines AI operation types."""

    GENERATE = "generate"
    """Generation operation."""

    STREAM = "stream"
    """Streaming operation."""

    EMBEDDING = "embedding"
    """Embedding operation."""


class AiErrorPhase(StrEnum):
    """Defines AI error phases."""

    REQUEST = "request"
    """Request phase."""

    RESPONSE = "response"
    """Response phase."""

    DECODE = "decode"
    """Decode phase."""

    RATE_LIMIT = "rate-limit"
    """Rate limit phase."""

    TOOL_CALL = "tool-call"
    """Tool call phase."""

    STREAM = "stream"
    """Stream phase."""


@dataclass(frozen=True)
class AiRetryImmediate:
    """Represents an immediate retry strategy."""

    pass


@dataclass(frozen=True)
class AiRetryExponential:
    """Represents an exponential backoff retry strategy."""

    pass


@dataclass(frozen=True)
class AiRetryAfter:
    """Represents a retry strategy with a specified delay."""

    delay_second: float
    """Delay in seconds before retrying."""


type AiRetryStrategy = AiRetryImmediate | AiRetryExponential | AiRetryAfter
"""Type alias for supported AI retry strategies."""


@dataclass(frozen=True)
class AiRetryResolution:
    """Represents a retry resolution for an AI error."""

    strategy: AiRetryStrategy
    """The retry strategy to apply."""


@dataclass(frozen=True)
class AiFallbackResolution:
    """Represents a fallback resolution for an AI error."""

    pass


@dataclass(frozen=True)
class AiFailResolution:
    """Represents a failure resolution for an AI error."""

    pass


type AiErrorResolution = AiRetryResolution | AiFallbackResolution | AiFailResolution
"""Type alias for AI error resolutions."""


class AiError(BaseError):
    """AI operation error."""

    def __init__(
        self,
        message: str,
        *,
        operation: AiOperation,
        model_key: str | None,
        model: str | None,
        phase: AiErrorPhase,
        resolution: AiErrorResolution,
        status_code: int | None = None,
        context: str | None = None,
        details: Mapping[str, object] | None = None,
    ) -> None:
        super().__init__(
            message,
            context=context,
            details=details,
        )
        self.operation = operation
        self.model_key = model_key
        self.model = model
        self.phase = phase
        self.resolution = resolution
        self.status_code = status_code
