from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Literal, Self
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class AiTextPart(BaseModel):
    """Represents a text content part within a message."""

    model_config = ConfigDict(frozen=True)
    type: Literal["text"] = "text"
    """Type discriminator field."""

    text: str
    """Text content."""


MessagePart = Annotated[
    AiTextPart,
    Field(discriminator="type"),
]
"""Represents a part of a message."""


class MessageRole(StrEnum):
    """Defines the role of a message sender."""

    assistant = "assistant"
    """Assistant role."""

    user = "user"
    """User role."""

    system = "system"
    """System role."""


class MessageSchema(BaseModel):
    """Represents a conversation message schema containing an ID, role, parts, and
    creation timestamp.
    """

    model_config = ConfigDict(frozen=True)
    id: UUID
    """Unique message identifier."""

    role: MessageRole
    """Role of the message sender."""

    parts: tuple[MessagePart, ...]
    """Collection of message parts."""

    created_at: datetime
    """Timestamp when the message was created."""

    @classmethod
    def user(cls, parts: tuple[MessagePart, ...]) -> Self:
        """Creates a user message with the specified parts."""

        return cls(
            id=(uuid4()),
            role=MessageRole.user,
            parts=parts,
            created_at=datetime.now(UTC),
        )

    @classmethod
    def user_text(cls, text: str) -> Self:
        """Creates a user message with a single text part."""

        return cls(
            id=(uuid4()),
            role=MessageRole.user,
            parts=(AiTextPart(type="text", text=text),),
            created_at=datetime.now(UTC),
        )

    @classmethod
    def system(cls, parts: tuple[MessagePart, ...]) -> Self:
        """Creates a system message with the specified parts."""

        return cls(
            id=(uuid4()),
            role=MessageRole.system,
            parts=parts,
            created_at=datetime.now(UTC),
        )

    @classmethod
    def system_text(cls, text: str) -> Self:
        """Creates a system message with a single text part."""

        return cls(
            id=(uuid4()),
            role=MessageRole.system,
            parts=(AiTextPart(type="text", text=text),),
            created_at=datetime.now(UTC),
        )

    @classmethod
    def assistant(cls, parts: tuple[MessagePart, ...]) -> Self:
        """Creates an assistant message with the specified parts."""

        return cls(
            id=(uuid4()),
            role=MessageRole.assistant,
            parts=parts,
            created_at=datetime.now(UTC),
        )

    @classmethod
    def assistant_text(cls, text: str) -> Self:
        """Creates an assistant message with a single text part."""

        return cls(
            id=(uuid4()),
            role=MessageRole.assistant,
            parts=(AiTextPart(type="text", text=text),),
            created_at=datetime.now(UTC),
        )
