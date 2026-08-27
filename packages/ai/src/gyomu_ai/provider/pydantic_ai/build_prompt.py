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
    instructions: AgentInstructions
    user_prompt: Sequence[UserContent]
    message_history: Sequence[ModelMessage] | None


def build_prompt(conversation: ConversationSchema) -> PydanticAiMessages:
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
    return ModelResponse(
        parts=list(map(_MessagePart2ModelResponsePart, message.parts)),
        timestamp=message.created_at,
    )


def _MessageSchema2ModelRequest(message: MessageSchema) -> ModelRequest:

    return ModelRequest(
        parts=list(map(_MessagePart2ModelRequestPart, message.parts)),
        timestamp=message.created_at,
    )


def _MessagePart2ModelResponsePart(message_part: MessagePart) -> ModelResponsePart:
    if isinstance(message_part, AiTextPart):
        return TextPart(
            message_part.text,
            part_kind="text",
        )
    raise ValueError(f"Non Supported Message: {message_part}")


def _MessagePart2ModelRequestPart(message_part: MessagePart) -> ModelRequestPart:
    if isinstance(message_part, AiTextPart):
        return UserPromptPart(
            message_part.text,
            part_kind="user-prompt",
        )
    raise ValueError(f"Non Supported Message: {message_part}")


def _MessagePart2UserContent(message_part: MessagePart) -> UserContent:
    if isinstance(message_part, AiTextPart):
        return TextContent(
            message_part.text,
            kind="text-content",
        )
    raise ValueError(f"Non Supported Message: {message_part}")


# def find_user_prompt(
#     sorted_messages: list[MessageSchema],
# ) -> tuple[Sequence[UserContent], int]:
#     result: list[UserContent] = []
#     last_user_result = next(
#         (
#             (i, sorted_messages[i])
#             for i in range(len(sorted_messages) - 1, -1, -1)
#             if sorted_messages[i].role == MessageRole.user
#         ),
#         None,
#     )

#     if last_user_result is None:
#         return result, -1
#     else:
#         return list(
#             map(_MessagePart2UserContent, last_user_result[1].parts)
#         ), last_user_result[0]


# def find_system_prompt(
#     sorted_messages: list[MessageSchema],
# ) -> tuple[list[str], int]:
#     result: list[str] = []
#     last_index = -1
#     for i, x in enumerate(sorted_messages):
#         if x.role == MessageRole.system:
#             result = [item.text for item in x.parts]
#             last_index = i
#             return result, last_index

#     return result, last_index
