from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Literal, Self
from uuid import UUID, uuid7

from pydantic import BaseModel, ConfigDict, Field


class MessageRole(StrEnum):
    assistant = "assistant"
    user = "user"
    system = "system"


class MessageSchema(BaseModel):
    model_config = ConfigDict(frozen=True)
    id: UUID
    role: MessageRole
    parts: tuple[MessagePart, ...]
    created_at: datetime

    @classmethod
    def user(cls, parts: tuple[MessagePart, ...]) -> Self:
        return cls(
            id=(uuid7()),
            role=MessageRole.user,
            parts=parts,
            created_at=datetime.now(UTC),
        )

    @classmethod
    def user_text(cls, text: str) -> Self:
        return cls(
            id=(uuid7()),
            role=MessageRole.user,
            parts=(AiTextPart(type="text", text=text),),
            created_at=datetime.now(UTC),
        )

    @classmethod
    def system(cls, parts: tuple[MessagePart, ...]) -> Self:
        return cls(
            id=(uuid7()),
            role=MessageRole.system,
            parts=parts,
            created_at=datetime.now(UTC),
        )

    @classmethod
    def system_text(cls, text: str) -> Self:
        return cls(
            id=(uuid7()),
            role=MessageRole.system,
            parts=(AiTextPart(type="text", text=text),),
            created_at=datetime.now(UTC),
        )

    @classmethod
    def assistant(cls, parts: tuple[MessagePart, ...]) -> Self:
        return cls(
            id=(uuid7()),
            role=MessageRole.assistant,
            parts=parts,
            created_at=datetime.now(UTC),
        )

    @classmethod
    def assistant_text(cls, text: str) -> Self:
        return cls(
            id=(uuid7()),
            role=MessageRole.assistant,
            parts=(AiTextPart(type="text", text=text),),
            created_at=datetime.now(UTC),
        )


class AiTextPart(BaseModel):
    model_config = ConfigDict(frozen=True)
    type: Literal["text"] = "text"
    text: str


MessagePart = Annotated[
    AiTextPart,
    Field(discriminator="type"),
]
