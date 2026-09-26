from collections.abc import Sequence
from dataclasses import dataclass

from gyomu_schema.conversation.conversation import ConversationSchema
from gyomu_schema.conversation.message import (
    AiTextPart,
    MessagePart,
    MessageRole,
    MessageSchema,
)
from pydantic_ai import (
    ModelMessage,
    ModelRequest,
    ModelRequestPart,
    ModelResponse,
    ModelResponsePart,
    TextContent,
    TextPart,
    UserContent,
    UserPromptPart,
)
from pydantic_ai.agent.abstract import AgentInstructions


@dataclass(frozen=True)
class PydanticAiMessages:
    """Encapsulates instructions, user prompt, and message history formatted for
    Pydantic AI.
    """

    instructions: AgentInstructions
    """Agent instructions for the conversation."""

    user_prompt: Sequence[UserContent]
    """User prompt content sequence."""

    message_history: Sequence[ModelMessage] | None
    """Optional sequence of previous model messages."""


def build_prompt(conversation: ConversationSchema) -> PydanticAiMessages:
    """Builds PydanticAI messages from a conversation schema.

    Args:
        conversation (ConversationSchema): The conversation schema containing request,
            system instructions, and history.

    Returns:
        PydanticAiMessages: Formatted PydanticAI messages structure.

    Raises:
        ValueError: Raised if conversation request is missing.
    """
    if not conversation.request:
        raise ValueError("messages must has user input")

    return PydanticAiMessages(
        instructions=list(map(lambda part: part.text, conversation.system.parts))
        if conversation.system is not None
        else None,
        user_prompt=list(
            map(lambda part: _MessagePart2UserContent(part), conversation.request.parts)
        ),
        message_history=list(
            map(
                lambda record: (
                    _MessageSchema2ModelRequest(record)
                    if record.role == MessageRole.user
                    else _MessageSchema2ModelResponse(record)
                ),
                conversation.messages,
            )
        )
        if len(conversation.messages) > 0
        else None,
    )


def _MessageSchema2ModelResponse(message: MessageSchema) -> ModelResponse:
    """Converts a message schema to a model response.

    Args:
        message (MessageSchema): The message schema to convert.

    Returns:
        ModelResponse: Converted ModelResponse object.
    """
    return ModelResponse(
        parts=list(map(_MessagePart2ModelResponsePart, message.parts)),
        timestamp=message.created_at,
    )


def _MessageSchema2ModelRequest(message: MessageSchema) -> ModelRequest:
    """Converts a message schema to a model request.

    Args:
        message (MessageSchema): The message schema to convert.

    Returns:
        ModelRequest: Converted ModelRequest object.
    """

    return ModelRequest(
        parts=list(map(_MessagePart2ModelRequestPart, message.parts)),
        timestamp=message.created_at,
    )


def _MessagePart2ModelResponsePart(message_part: MessagePart) -> ModelResponsePart:
    """Converts a message part to a model response part.

    Args:
        message_part (MessagePart): The message part to convert.

    Returns:
        ModelResponsePart: Converted model response part.

    Raises:
        ValueError: Raised if the message part type is not supported.
    """
    if isinstance(message_part, AiTextPart):
        return TextPart(
            message_part.text,
            part_kind="text",
        )
    raise ValueError(f"Non Supported Message: {message_part}")


def _MessagePart2ModelRequestPart(message_part: MessagePart) -> ModelRequestPart:
    """Converts a message part to a model request part.

    Args:
        message_part (MessagePart): The message part to convert.

    Returns:
        ModelRequestPart: Converted model request part.

    Raises:
        ValueError: Raised if the message part type is not supported.
    """
    if isinstance(message_part, AiTextPart):
        return UserPromptPart(
            message_part.text,
            part_kind="user-prompt",
        )
    raise ValueError(f"Non Supported Message: {message_part}")


def _MessagePart2UserContent(message_part: MessagePart) -> UserContent:
    """Converts a message part to user content.

    Args:
        message_part (MessagePart): The message part to convert.

    Returns:
        UserContent: Converted user content.

    Raises:
        ValueError: Raised if the message part type is not supported.
    """
    if isinstance(message_part, AiTextPart):
        return TextContent(
            message_part.text,
            kind="text-content",
        )
    raise ValueError(f"Non Supported Message: {message_part}")
