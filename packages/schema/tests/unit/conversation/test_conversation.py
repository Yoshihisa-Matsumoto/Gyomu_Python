import pytest
from gyomu_schema.conversation.conversation import ConversationSchema
from gyomu_schema.conversation.message import (
    MessageRole,
    MessageSchema,
)
from pydantic import ValidationError


def create_message(
    role: MessageRole,
    text: str,
) -> MessageSchema:
    match role:
        case MessageRole.user:
            return MessageSchema.user_text(text)
        case MessageRole.system:
            return MessageSchema.system_text(text)
        case MessageRole.assistant:
            return MessageSchema.assistant_text(text)


class TestConversationSchema:
    def test_with_request(self) -> None:
        user = create_message(
            MessageRole.user,
            "Hello",
        )
        conversation = ConversationSchema()

        result = conversation.with_request(user)

        assert result.system is None
        assert result.messages == ()
        assert result.request == user

        # 元のConversationは変更されない
        assert conversation.request is None

    def test_with_request_rejects_non_user_message(self) -> None:
        assistant = create_message(
            MessageRole.assistant,
            "Hello",
        )
        conversation = ConversationSchema()

        with pytest.raises(
            ValueError,
            match="request must be a user message",
        ):
            conversation.with_request(assistant)

    def test_with_request_rejects_existing_request(self) -> None:
        first_request = create_message(
            MessageRole.user,
            "Hello",
        )
        second_request = create_message(
            MessageRole.user,
            "How are you?",
        )

        conversation = ConversationSchema().with_request(first_request)

        with pytest.raises(
            ValueError,
            match="request already exists",
        ):
            conversation.with_request(second_request)

    def test_complete(self) -> None:
        user = create_message(
            MessageRole.user,
            "Hello",
        )
        assistant = create_message(
            MessageRole.assistant,
            "Hello!",
        )
        conversation = ConversationSchema().with_request(user)

        result = conversation.complete(assistant)

        assert result.system is None
        assert result.messages == (
            user,
            assistant,
        )
        assert result.request is None

        # 元のConversationは変更されない
        assert conversation.messages == ()
        assert conversation.request == user

    def test_complete_preserves_existing_messages(self) -> None:
        previous_user = create_message(
            MessageRole.user,
            "First question",
        )
        previous_assistant = create_message(
            MessageRole.assistant,
            "First answer",
        )
        current_user = create_message(
            MessageRole.user,
            "Second question",
        )
        current_assistant = create_message(
            MessageRole.assistant,
            "Second answer",
        )

        conversation = ConversationSchema(
            system=None,
            messages=(
                previous_user,
                previous_assistant,
            ),
            request=current_user,
        )

        result = conversation.complete(current_assistant)

        assert result.messages == (
            previous_user,
            previous_assistant,
            current_user,
            current_assistant,
        )
        assert result.request is None

    def test_complete_rejects_missing_request(self) -> None:
        assistant = create_message(
            MessageRole.assistant,
            "Hello!",
        )
        conversation = ConversationSchema()

        with pytest.raises(
            ValueError,
            match="request does not exist",
        ):
            conversation.complete(assistant)

    def test_complete_rejects_non_assistant_message(self) -> None:
        user = create_message(
            MessageRole.user,
            "Hello",
        )
        another_user = create_message(
            MessageRole.user,
            "How are you?",
        )
        conversation = ConversationSchema().with_request(user)

        with pytest.raises(
            ValueError,
            match="response must be an assistant message",
        ):
            conversation.complete(another_user)

    def test_is_immutable(self) -> None:
        user = create_message(
            MessageRole.user,
            "Hello",
        )
        conversation = ConversationSchema(
            system=None,
            messages=(),
            request=None,
        )

        with pytest.raises(ValidationError):
            conversation.request = user

    def test_messages_are_immutable(self) -> None:
        user = create_message(
            MessageRole.user,
            "Hello",
        )
        conversation = ConversationSchema(
            system=None,
            messages=(user,),
            request=None,
        )

        with pytest.raises(ValidationError):
            conversation.messages = ()

    def test_model_serialization_and_deserialization(self) -> None:
        user = create_message(
            MessageRole.user,
            "Hello",
        )
        conversation = ConversationSchema().with_request(user)

        json_data = conversation.model_dump_json()

        restored = ConversationSchema.model_validate_json(json_data)

        assert restored == conversation
        assert restored.request == user
