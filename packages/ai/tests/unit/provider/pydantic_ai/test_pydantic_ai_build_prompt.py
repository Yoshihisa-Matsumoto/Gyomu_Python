from datetime import UTC, datetime

import pytest
from gyomu_ai.provider.pydantic_ai.build_prompt import build_prompt
from gyomu_schema.conversation.conversation import ConversationSchema
from gyomu_schema.conversation.message import (
    AiTextPart,
    MessageRole,
    MessageSchema,
)
from pydantic_ai import (
    ModelRequest,
    ModelResponse,
    TextContent,
    TextPart,
    UserPromptPart,
)


class TestBuildPrompt:
    def test_builds_prompt_without_system_and_history(
        self,
    ) -> None:
        request = MessageSchema(
            role=MessageRole.user,
            parts=[
                AiTextPart(type="text", text="Hello"),
            ],
            id="1",
            created_at=datetime(
                2026,
                10,
                1,
            ),
        )

        conversation = ConversationSchema(
            system=None,
            messages=(),
            request=request,
        )

        result = build_prompt(conversation)

        assert result.instructions is None
        assert len(result.user_prompt) == 1
        user_content = result.user_prompt[0]
        assert isinstance(user_content, TextContent)
        if isinstance(user_content, TextContent):
            assert user_content.content == "Hello"
        assert result.message_history is None

    def test_builds_system_instructions(
        self,
    ) -> None:
        system = MessageSchema(
            id="1",
            role=MessageRole.system,
            parts=[
                AiTextPart(type="text", text="You are an assistant."),
                AiTextPart(type="text", text="Answer concisely."),
            ],
            created_at=datetime(
                2026,
                10,
                1,
            ),
        )
        request = MessageSchema(
            id="2",
            role=MessageRole.user,
            parts=[AiTextPart(type="text", text="Hello")],
            created_at=datetime(
                2026,
                10,
                2,
            ),
        )

        conversation = ConversationSchema(
            system=system,
            messages=(),
            request=request,
        )

        result = build_prompt(conversation)

        assert result.instructions == [
            "You are an assistant.",
            "Answer concisely.",
        ]

    def test_builds_user_prompt_from_multiple_parts(
        self,
    ) -> None:
        request = MessageSchema(
            id="1",
            role=MessageRole.user,
            parts=[
                AiTextPart(type="text", text="Hello"),
                AiTextPart(type="text", text="How are you?"),
            ],
            created_at=datetime(
                2026,
                10,
                2,
            ),
        )

        conversation = ConversationSchema(
            system=None,
            messages=(),
            request=request,
        )

        result = build_prompt(conversation)

        assert result.user_prompt == [
            TextContent("Hello"),
            TextContent("How are you?"),
        ]

    def test_builds_user_message_history(
        self,
    ) -> None:
        created_at = datetime.now(UTC)

        message = MessageSchema(
            id="1",
            role=MessageRole.user,
            parts=[
                AiTextPart(type="text", text="Hello"),
            ],
            created_at=created_at,
        )

        conversation = ConversationSchema(
            system=None,
            messages=(message,),
            request=MessageSchema(
                id="2",
                role=MessageRole.user,
                parts=[AiTextPart(type="text", text="Next")],
                created_at=created_at,
            ),
        )

        result = build_prompt(conversation)

        assert result.message_history is not None
        assert len(result.message_history) == 1

        history = result.message_history[0]

        assert isinstance(history, ModelRequest)
        assert history.timestamp == created_at
        assert len(history.parts) == 1

        part = history.parts[0]

        assert isinstance(part, UserPromptPart)
        assert part.content == "Hello"

    def test_builds_assistant_message_history(
        self,
    ) -> None:
        created_at = datetime.now(UTC)

        message = MessageSchema(
            id="1",
            role=MessageRole.assistant,
            parts=[
                AiTextPart(type="text", text="Hello!"),
            ],
            created_at=created_at,
        )

        conversation = ConversationSchema(
            system=None,
            messages=(message,),
            request=MessageSchema(
                id="2",
                role=MessageRole.user,
                parts=[
                    AiTextPart(type="text", text="Next"),
                ],
                created_at=datetime(
                    2026,
                    10,
                    2,
                ),
            ),
        )

        result = build_prompt(conversation)

        assert result.message_history is not None
        assert len(result.message_history) == 1

        history = result.message_history[0]

        assert isinstance(history, ModelResponse)
        assert history.timestamp == created_at
        assert history.parts == [
            TextPart("Hello!"),
        ]

    def test_builds_mixed_message_history(
        self,
    ) -> None:
        created_at = datetime.now(UTC)
        user_message = MessageSchema(
            id="1",
            role=MessageRole.user,
            parts=[AiTextPart(type="text", text="Question")],
            created_at=created_at,
        )
        assistant_message = MessageSchema(
            id="2",
            role=MessageRole.assistant,
            parts=[
                AiTextPart(type="text", text="Answer"),
            ],
            created_at=created_at,
        )

        conversation = ConversationSchema(
            system=None,
            messages=(user_message, assistant_message),
            request=MessageSchema(
                id="3",
                role=MessageRole.user,
                parts=[AiTextPart(type="text", text="Follow-up")],
                created_at=created_at,
            ),
        )

        result = build_prompt(conversation)

        assert result.message_history is not None
        assert len(result.message_history) == 2

        history1 = result.message_history[0]
        history2 = result.message_history[1]

        assert isinstance(history1, ModelRequest)
        if isinstance(history1, ModelRequest):
            assert history1.timestamp == created_at
            assert len(history1.parts) == 1

            part = history1.parts[0]

            assert isinstance(part, UserPromptPart)
            assert part.content == "Question"

        assert isinstance(history2, ModelResponse)
        if isinstance(history2, ModelResponse):
            assert history2.timestamp == created_at
            assert len(history2.parts) == 1

            part = history2.parts[0]

            assert isinstance(part, TextPart)
            assert part.content == "Answer"

    def test_rejects_conversation_without_request(
        self,
    ) -> None:
        conversation = ConversationSchema(
            system=None,
            messages=(),
            request=None,
        )

        with pytest.raises(
            ValueError,
            match="messages must has user input",
        ):
            build_prompt(conversation)
