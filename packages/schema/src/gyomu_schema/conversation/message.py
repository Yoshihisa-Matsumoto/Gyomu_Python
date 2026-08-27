from datetime import datetime
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, Field


class MessageRole(StrEnum):
    assistant = "assistant"
    user = "user"
    system = "system"


class MessageSchema(BaseModel):
    id: str
    role: MessageRole
    parts: list[MessagePart]
    created_at: datetime


class AiTextPart(BaseModel):
    type: Literal["text"]
    text: str


MessagePart = Annotated[
    AiTextPart,
    Field(discriminator="type"),
]
