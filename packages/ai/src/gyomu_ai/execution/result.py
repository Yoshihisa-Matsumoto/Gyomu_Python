from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel


@dataclass(frozen=True)
class AiToolCallResultPart:
    tool_name: str
    tool_call_id: str
    input: Any


@dataclass(frozen=True)
class AiTextResultPart:
    text: str


@dataclass(frozen=True)
class AiTextDeltaResultPart:
    text: str


type AiMessagePart = AiTextResultPart | AiToolCallResultPart
type AiStreamEvent = AiTextDeltaResultPart | AiToolCallResultPart


@dataclass(frozen=True)
class AiAssistantMessage:
    parts: list[AiMessagePart]
    text: str


AiFinishReason = Literal[
    "completed",
    "max-tokens",
    "tool-call",
    "content-filtered",
    "error",
    "cancelled",
    "unknown",
]


@dataclass(frozen=True)
class AiUsage:
    input_tokens: int
    output_tokens: int
    total_tokens: int


@dataclass(frozen=True)
class AiGenerationMetadata:
    started_at: datetime
    completed_at: datetime
    elapsed_second: float
    usage: AiUsage
    finish_reason: AiFinishReason | None


@dataclass(frozen=True)
class AiGenerateTextResult:
    message: AiAssistantMessage
    metadata: AiGenerationMetadata


@dataclass(frozen=True)
class AiGenerateObjectResult[T: BaseModel]:
    output: T
    metadata: AiGenerationMetadata


@dataclass(frozen=True)
class AiTextStream:
    pass


@dataclass(frozen=True)
class AiEmbeddingResult:
    vector: Sequence[Sequence[float]]
    metadata: AiGenerationMetadata
