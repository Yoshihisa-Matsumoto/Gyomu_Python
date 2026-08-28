from dataclasses import dataclass
from enum import StrEnum
from typing import Literal

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
    type: Literal["immediate"] = "immediate"


@dataclass(frozen=True)
class AiRetryExponential:
    type: Literal["exponential"] = "exponential"


@dataclass(frozen=True)
class AiRetryAfter:
    delay_second: float
    type: Literal["retry-after"] = "retry-after"


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

    operation: AiOperation
    model_key: str | None
    model: str | None
    phase: AiErrorPhase
    resolution: AiErrorResolution
    status_code: int | None = None
