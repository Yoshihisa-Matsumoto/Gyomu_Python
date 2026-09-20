from typing import Self

from pydantic import BaseModel, ConfigDict

from gyomu_schema.conversation.message import MessageRole, MessageSchema


class ConversationSchema(BaseModel):
    """Defines a conversation schema with system message, message history, and request
    state.

    Represents a conversation consisting of an optional system prompt, a history of
    messages, and an active request message.
    """

    model_config = ConfigDict(frozen=True)

    system: MessageSchema | None = None
    """Optional system message defining the conversation context or behavior."""

    messages: tuple[MessageSchema, ...] = ()
    """Sequence of historical messages exchanged in the conversation."""

    request: MessageSchema | None = None
    """Active request message awaiting completion."""

    def with_request(
        self,
        request: MessageSchema,
    ) -> Self:
        """Adds a new user request message to the conversation.

        Args:
            request (MessageSchema): The user message to set as the active request.

        Returns:
            Self: A new conversation instance with the added request.

        Raises:
            ValueError: If the request role is not user, or if a request already exists.
        """
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
        """Completes the current request with an assistant response and updates message
        history.

        Args:
            response (MessageSchema): The assistant response message to complete the
                conversation turn.

        Returns:
            Self: A new conversation instance containing the completed turn.

        Raises:
            ValueError: If no request exists, or if the response role is not assistant.
        """
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
