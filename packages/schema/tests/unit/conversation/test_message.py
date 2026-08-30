from datetime import UTC, datetime
from uuid import UUID

import pytest
from gyomu_schema.conversation.message import (
    AiTextPart,
    MessageRole,
    MessageSchema,
)
from pydantic import ValidationError


class TestMessageSchemaFactory:
    def test_is_frozen(self) -> None:
        message = MessageSchema.user_text("Hello")

        with pytest.raises(ValidationError):
            message.role = MessageRole.assistant

    def test_user(self) -> None:
        part = AiTextPart(text="Hello")

        before = datetime.now(UTC)
        message = MessageSchema.user(parts=(part,))
        after = datetime.now(UTC)

        assert message.role == MessageRole.user
        assert message.parts == (part,)

        assert isinstance(message.id, UUID)
        assert message.created_at >= before
        assert message.created_at <= after

    def test_assistant(self) -> None:
        part = AiTextPart(text="Hello")

        message = MessageSchema.assistant(parts=(part,))

        assert message.role == MessageRole.assistant
        assert message.parts == (part,)
        assert isinstance(message.id, UUID)

    def test_system(self) -> None:
        part = AiTextPart(text="You are a helpful assistant.")

        message = MessageSchema.system(parts=(part,))

        assert message.role == MessageRole.system
        assert message.parts == (part,)
        assert isinstance(message.id, UUID)

    def test_user_text(self) -> None:
        message = MessageSchema.user_text("Hello")

        assert message.role == MessageRole.user
        assert message.parts == (AiTextPart(text="Hello"),)

    def test_assistant_text(self) -> None:
        message = MessageSchema.assistant_text("Hello")

        assert message.role == MessageRole.assistant
        assert message.parts == (AiTextPart(text="Hello"),)

    def test_system_text(self) -> None:
        message = MessageSchema.system_text("Hello")

        assert message.role == MessageRole.system
        assert message.parts == (AiTextPart(text="Hello"),)
