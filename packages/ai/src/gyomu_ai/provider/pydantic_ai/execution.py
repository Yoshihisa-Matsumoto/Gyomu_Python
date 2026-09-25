import asyncio
from collections.abc import Awaitable, Callable

from gyomu_ai.execution.context import AiExecutionContext, AiModelContext
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
from gyomu_ai.provider.pydantic_ai.create_agent import (
    create_pydantic_ai_agent,
    create_pydantic_ai_agent_for_object,
)
from gyomu_ai.provider.pydantic_ai.map_error import map_pydantic_ai_error
from gyomu_ai.provider.pydantic_ai.map_result import (
    map_embed_result,
    map_generate_object_result,
    map_generate_text_result,
)
from gyomu_ai.provider.pydantic_ai.model_settings import build_model_settings
from gyomu_ai.provider.pydantic_ai.stream import PydanticAiTextStream
from gyomu_schema.conversation.conversation import ConversationSchema
from gyomu_schema.error.ai import (
    AiError,
    AiOperation,
    AiRetryAfter,
    AiRetryExponential,
    AiRetryImmediate,
    AiRetryResolution,
    AiRetryStrategy,
)
from gyomu_schema.option.retry import RetryParameter
from gyomu_schema.utility.execution_timer import ExecutionTimer
from pydantic import BaseModel
from pydantic_ai import Embedder, EmbeddingModel
from pydantic_ai.models import Model
from returns.result import Failure, Result, Success


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

    async def _execute[T](
        self,
        operation: AiOperation,
        model: str | None,
        model_key: str | None,
        action: Callable[[], Awaitable[T]],
    ) -> Result[T, AiError]:
        try:
            return Success(await action())
        except BaseException as error:
            return Failure(
                map_pydantic_ai_error(
                    error, operation=operation, model_key=model_key, model=model
                )
            )

    async def _execute_with_retry[T](
        self,
        operation: AiOperation,
        model: str | None,
        model_key: str | None,
        action: Callable[[], Awaitable[T]],
        execution: AiExecutionContext | None,
    ) -> Result[T, AiError]:
        retry_option = execution.retry_option if execution is not None else None

        max_attempts = (
            retry_option.max_attempts
            if retry_option is not None and retry_option.max_attempts is not None
            else 3
        )

        retry_count = 0

        while True:
            result = await self._execute(
                operation,
                model=model,
                model_key=model_key,
                action=action,
            )

            if isinstance(result, Success):
                return result

            error = result.failure()

            if not isinstance(error.resolution, AiRetryResolution):
                return Failure(error)

            if retry_count >= max_attempts:
                return Failure(error)

            delay_milliseconds = self._calculate_retry_delay_milliseconds(
                error.resolution.strategy, retry_count
            )

            if retry_option is not None and retry_option.observer is not None:
                retry_option.observer.on_retry(
                    RetryParameter(
                        error=error,
                        attempt=retry_count,
                        delay_milliseconds=delay_milliseconds,
                    )
                )

            if delay_milliseconds > 0:
                await asyncio.sleep(delay_milliseconds / 1000)

            retry_count += 1

    def _calculate_retry_delay_milliseconds(
        self,
        strategy: AiRetryStrategy,
        attempt: int,
    ) -> int:
        match strategy:
            case AiRetryImmediate():
                return 0

            case AiRetryAfter(delay_second=delay_second):
                return int(delay_second * 1000)

            case AiRetryExponential():
                return min(
                    1000 * 2**attempt,
                    60_000,
                )

    def _calculate_exponential_retry_delay(
        self,
        retry_count: int,
    ) -> float:
        return float(2**retry_count)

    async def _generate_text(
        self,
        model: Model,
        conversation: ConversationSchema,
        params: GenerateTextParams,
    ) -> AiGenerateTextResult:
        agent, usage_limits = create_pydantic_ai_agent(model, params.tool)
        prompt = build_prompt(conversation)
        timer = ExecutionTimer.start()
        response = await agent.run(
            instructions=prompt.instructions,
            user_prompt=prompt.user_prompt,
            message_history=prompt.message_history,
            model_settings=build_model_settings(params.execution),
            usage_limits=usage_limits,
        )

        return map_generate_text_result(timer, response, conversation)

    async def generate_text(
        self,
        conversation: ConversationSchema,
        params: GenerateTextParams,
    ) -> Result[AiGenerateTextResult, AiError]:
        model = self._select_model(params.key, params.execution)
        return await self._execute_with_retry(
            AiOperation.GENERATE,
            model=model.model_name,
            model_key=params.key,
            action=lambda: self._generate_text(
                model,
                conversation,
                params,
            ),
            execution=params.execution,
        )

    async def _stream_text(
        self,
        model: Model,
        conversation: ConversationSchema,
        params: StreamTextParams,
    ) -> AiTextStream:
        agent, usage_limits = create_pydantic_ai_agent(model, params.tool)
        prompt = build_prompt(conversation)
        timer = ExecutionTimer.start()
        response = agent.run_stream(
            instructions=prompt.instructions,
            user_prompt=prompt.user_prompt,
            message_history=prompt.message_history,
            model_settings=build_model_settings(params.execution),
            usage_limits=usage_limits,
        )
        return PydanticAiTextStream(
            response,
            conversation,
            timer,
            model=model.model_name,
            model_key=str(params.key),
        )

    async def stream_text(
        self,
        conversation: ConversationSchema,
        params: StreamTextParams,
    ) -> Result[AiTextStream, AiError]:
        model = self._select_model(params.key, params.execution)
        return await self._execute_with_retry(
            AiOperation.STREAM,
            model=model.model_name,
            model_key=params.key,
            action=lambda: self._stream_text(
                model,
                conversation,
                params,
            ),
            execution=params.execution,
        )

    async def _generate_object[T: BaseModel](
        self,
        model: Model,
        conversation: ConversationSchema,
        params: GenerateObjectParams[T],
    ) -> AiGenerateObjectResult[T]:
        agent, usage_limits = create_pydantic_ai_agent_for_object(
            model, params.output_type, params.tool
        )
        # agent2=  Agent(model=model, output_type=params.output_type)
        prompt = build_prompt(conversation)
        timer = ExecutionTimer.start()
        response = await agent.run(
            instructions=prompt.instructions,
            user_prompt=prompt.user_prompt,
            message_history=prompt.message_history,
            model_settings=build_model_settings(params.execution),
            usage_limits=usage_limits,
        )

        return map_generate_object_result(timer, response)

    async def generate_object[T: BaseModel](
        self,
        conversation: ConversationSchema,
        params: GenerateObjectParams[T],
    ) -> Result[AiGenerateObjectResult[T], AiError]:
        model = self._select_model(params.key, params.execution)
        return await self._execute_with_retry(
            AiOperation.GENERATE,
            model=model.model_name,
            model_key=params.key,
            action=lambda: self._generate_object(
                model,
                conversation,
                params,
            ),
            execution=params.execution,
        )

    async def _embed[T](
        self,
        agent: Embedder,
        params: EmbedParams[T],
    ) -> AiEmbeddingResult:

        timer = ExecutionTimer.start()
        response = await agent.embed(
            str(params.value),
            input_type="document" if params.mode == "document" else "query",
        )
        return map_embed_result(timer, response)

    async def embed[T](
        self,
        params: EmbedParams[T],
    ) -> Result[AiEmbeddingResult, AiError]:
        embedder = self._registry.embedding(params.execution)
        model_name: str = ""
        if isinstance(embedder.model, EmbeddingModel):
            model_name = embedder.model.model_name
        else:
            model_name = embedder.model
        return await self._execute_with_retry(
            AiOperation.EMBEDDING,
            model=model_name,
            model_key=AiModelKey.EMBEDDING,
            action=lambda: self._embed(
                embedder,
                params,
            ),
            execution=params.execution,
        )
