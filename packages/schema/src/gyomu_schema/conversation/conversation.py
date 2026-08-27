from typing import Self

from pydantic import BaseModel, ConfigDict

from gyomu_schema.conversation.message import MessageRole, MessageSchema


class ConversationSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    system: MessageSchema | None
    messages: tuple[MessageSchema, ...]
    request: MessageSchema | None

    def with_request(
        self,
        request: MessageSchema,
    ) -> Self:
        if request.role != MessageRole.user:
            raise ValueError("request must be a user message")

        if self.request is not None:
            raise ValueError("request already exists")

        return self.model_copy(
            update={"request": request},
        )

    def complete(
        self,
        response: MessageSchema,
    ) -> Self:
        if self.request is None:
            raise ValueError("request does not exist")

        if response.role != MessageRole.assistant:
            raise ValueError("response must be an assistant message")

        return self.model_copy(
            update={
                "messages": (
                    *self.messages,
                    self.request,
                    response,
                ),
                "request": None,
            },
        )
