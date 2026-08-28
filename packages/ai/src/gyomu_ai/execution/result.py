from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from types import TracebackType
from typing import Any, Literal, Protocol, Self

from gyomu_schema.conversation.conversation import ConversationSchema
from gyomu_schema.conversation.message import AiTextPart, MessageSchema
from pydantic import BaseModel


@dataclass(frozen=True)
class AiToolCallResultPart:
    tool_name: str
    tool_call_id: str
    input: Any


@dataclass(frozen=True)
class AiTextDeltaResultPart:
    text: str


type AiMessagePart = AiTextPart | AiToolCallResultPart
type AiStreamEvent = AiTextDeltaResultPart | AiToolCallResultPart


@dataclass(frozen=True)
class AiAssistantTextMessage:
    parts: tuple[AiMessagePart, ...]
    text: str

    @classmethod
    def from_message(
        cls,
        message: MessageSchema,
    ) -> Self:
        text = "\r\n".join(
            part.text for part in message.parts if isinstance(part, AiTextPart)
        )
        return cls(parts=message.parts, text=text)


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
    message: AiAssistantTextMessage
    metadata: AiGenerationMetadata
    conversation: ConversationSchema


@dataclass(frozen=True)
class AiGenerateObjectResult[T: BaseModel]:
    output: T
    metadata: AiGenerationMetadata


class AiTextStream(Protocol):
    async def __aenter__(self) -> Self: ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...

    def __aiter__(self) -> Self: ...

    async def __anext__(self) -> str: ...

    @property
    def result(self) -> AiGenerateTextResult | None: ...


@dataclass(frozen=True)
class AiEmbeddingResult:
    vector: Sequence[Sequence[float]]
    metadata: AiGenerationMetadata
