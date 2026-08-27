from collections.abc import Sequence
from typing import Protocol

from gyomu_schema.conversation.conversation import ConversationSchema
from gyomu_schema.error.ai import AiError
from pydantic import BaseModel
from returns.result import Result

from gyomu_ai.execution.parameter import (
    EmbedParams,
    GenerateObjectParams,
    GenerateTextParams,
    StreamTextParams,
)
from gyomu_ai.execution.result import AiGenerateTextResult, AiTextStream


class AiModelExecution(Protocol):
    async def generate_text(
        self,
        conversation: ConversationSchema,
        params: GenerateTextParams,
    ) -> Result[AiGenerateTextResult, AiError]: ...

    async def generate_object[T: BaseModel](
        self,
        conversation: ConversationSchema,
        params: GenerateObjectParams[T],
    ) -> Result[T, AiError]: ...

    async def stream_text(
        self,
        conversation: ConversationSchema,
        params: StreamTextParams,
    ) -> Result[AiTextStream, AiError]: ...

    async def embed[T](
        self,
        params: EmbedParams[T],
    ) -> Result[Sequence[float], AiError]: ...
