from gyomu_ai.execution.context import AiModelContext
from gyomu_ai.execution.parameter import (
    EmbedParams,
    GenerateObjectParams,
    GenerateTextParams,
    StreamTextParams,
)
from gyomu_ai.execution.result import (
    AiEmbeddingResult,
    AiGenerateObjectResult,
    AiGenerateTextResult,
    AiTextStream,
)
from gyomu_ai.model.ai_model import AiModelKey
from gyomu_ai.provider.pydantic_ai.ai_model import PydanticAiModelRegistry
from gyomu_ai.provider.pydantic_ai.build_prompt import build_prompt
from gyomu_ai.provider.pydantic_ai.map_result import (
    map_embed_result,
    map_generate_object_result,
    map_generate_text_result,
)
from gyomu_ai.provider.pydantic_ai.model_settings import build_model_settings
from gyomu_ai.provider.pydantic_ai.result import PydanticAiTextStream
from gyomu_schema.conversation.conversation import ConversationSchema
from gyomu_schema.error.ai import AiError
from gyomu_schema.utility.execution_timer import ExecutionTimer
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models import Model
from returns.result import Result, Success


class PydanticAiModelExecution:
    def __init__(
        self,
        registry: PydanticAiModelRegistry,
    ) -> None:
        self._registry = registry

    def _select_model(self, key: AiModelKey, context: AiModelContext | None) -> Model:
        match key:
            case AiModelKey.FAST:
                return self._registry.fast(context)
            case AiModelKey.SMART:
                return self._registry.smart(context)
            case AiModelKey.REASONING:
                return self._registry.reasoning(context)
            case AiModelKey.VISION:
                return self._registry.vision(context)
            case AiModelKey.EMBEDDING:
                raise ValueError("Embedding model cannot be used for text generation")

    async def generate_text(
        self,
        conversation: ConversationSchema,
        params: GenerateTextParams,
    ) -> Result[AiGenerateTextResult, AiError]:
        model = self._select_model(params.key, params.execution)
        agent = Agent(model=model)
        prompt = build_prompt(conversation)
        timer = ExecutionTimer.start()
        response = await agent.run(
            instructions=prompt.instructions,
            user_prompt=prompt.user_prompt,
            message_history=prompt.message_history,
            model_settings=build_model_settings(params.execution),
        )

        return Success(map_generate_text_result(timer, response, conversation))

    async def stream_text(
        self,
        conversation: ConversationSchema,
        params: StreamTextParams,
    ) -> Result[AiTextStream, AiError]:
        model = self._select_model(params.key, params.execution)
        agent = Agent(model=model)
        prompt = build_prompt(conversation)
        timer = ExecutionTimer.start()
        response = agent.run_stream(
            instructions=prompt.instructions,
            user_prompt=prompt.user_prompt,
            message_history=prompt.message_history,
            model_settings=build_model_settings(params.execution),
        )
        return Success(PydanticAiTextStream(response, conversation, timer))

    async def generate_object[T: BaseModel](
        self,
        conversation: ConversationSchema,
        params: GenerateObjectParams[T],
    ) -> Result[AiGenerateObjectResult[T], AiError]:
        model = self._select_model(params.key, params.execution)
        agent = Agent(model=model, output_type=params.output_type)
        prompt = build_prompt(conversation)
        timer = ExecutionTimer.start()
        response = await agent.run(
            instructions=prompt.instructions,
            user_prompt=prompt.user_prompt,
            message_history=prompt.message_history,
            model_settings=build_model_settings(params.execution),
        )

        return Success(map_generate_object_result(timer, response))

    async def embed[T](
        self,
        params: EmbedParams[T],
    ) -> Result[AiEmbeddingResult, AiError]:
        agent = self._registry.embedding(params.execution)

        timer = ExecutionTimer.start()
        response = await agent.embed(
            str(params.value),
            input_type="document" if params.mode == "document" else "query",
        )
        return Success(map_embed_result(timer, response))
