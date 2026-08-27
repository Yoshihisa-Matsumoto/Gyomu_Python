from dataclasses import dataclass
from typing import Any, Literal


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
class AiGenerateTextResult:
    message: AiAssistantMessage
    usage: AiUsage | None
    finish_reason: AiFinishReason | None


@dataclass(frozen=True)
class AiTextStream:
    pass
