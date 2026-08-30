from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum

from gyomu_schema.error.base import BaseError


class AiOperation(StrEnum):
    GENERATE = "generate"
    STREAM = "stream"
    EMBEDDING = "embedding"


class AiErrorPhase(StrEnum):
    REQUEST = "request"
    RESPONSE = "response"
    DECODE = "decode"
    RATE_LIMIT = "rate-limit"
    TOOL_CALL = "tool-call"
    STREAM = "stream"


@dataclass(frozen=True)
class AiRetryImmediate:
    pass


@dataclass(frozen=True)
class AiRetryExponential:
    pass


@dataclass(frozen=True)
class AiRetryAfter:
    delay_second: float


type AiRetryStrategy = AiRetryImmediate | AiRetryExponential | AiRetryAfter


@dataclass(frozen=True)
class AiRetryResolution:
    strategy: AiRetryStrategy


@dataclass(frozen=True)
class AiFallbackResolution:
    pass


@dataclass(frozen=True)
class AiFailResolution:
    pass


type AiErrorResolution = AiRetryResolution | AiFallbackResolution | AiFailResolution


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
