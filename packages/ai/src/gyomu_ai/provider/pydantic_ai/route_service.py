from collections.abc import Awaitable, Callable

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
from gyomu_ai.provider.pydantic_ai.execution import PydanticAiModelExecution
from gyomu_ai.provider.pydantic_ai.route_registry import _get_model_route
from gyomu_ai.provider.pydantic_ai.routing import (
    ModelRouteId,
    ModelRouteTableId,
    RouteNode,
)
from gyomu_schema.conversation.conversation import ConversationSchema
from gyomu_schema.error.ai import AiError, AiFallbackResolution
from pydantic import BaseModel
from returns.result import Failure, Result, Success


class PydanticAiRoutingExecution:
    def __init__(
        self,
        route_id: ModelRouteId,
        route_table_id: ModelRouteTableId | None = None,
    ) -> None:
        self.route = _get_model_route(route_id=route_id, route_table_id=route_table_id)

    async def run_node[A](
        self,
        node: RouteNode,
        execute: Callable[
            [PydanticAiModelExecution],
            Awaitable[Result[A, AiError]],
        ],
    ) -> Result[A, AiError]:
        return await execute(
            PydanticAiModelExecution(node.registry, retry_option=node.retry_option)
        )

    async def run_with_model_route[A](
        self,
        execute: Callable[
            [PydanticAiModelExecution],
            Awaitable[Result[A, AiError]],
        ],
    ) -> Result[A, AiError]:
        last_error: AiError | None = None

        for node in self.route.nodes:
            result = await self.run_node(node, execute)

            if isinstance(result, Success):
                return result

            last_error = result.failure()

            if not isinstance(last_error.resolution, AiFallbackResolution):
                return Failure(last_error)

        assert last_error is not None
        return Failure(last_error)

    async def generate_text(
        self,
        conversation: ConversationSchema,
        params: GenerateTextParams,
    ) -> Result[AiGenerateTextResult, AiError]:

        return await self.run_with_model_route(
            lambda service: service.generate_text(conversation, params)
        )

    async def stream_text(
        self,
        conversation: ConversationSchema,
        params: StreamTextParams,
    ) -> Result[AiTextStream, AiError]:

        return await self.run_with_model_route(
            lambda service: service.stream_text(conversation, params)
        )

    async def generate_object[T: BaseModel](
        self,
        conversation: ConversationSchema,
        params: GenerateObjectParams[T],
    ) -> Result[AiGenerateObjectResult[T], AiError]:

        return await self.run_with_model_route(
            lambda service: service.generate_object(conversation, params)
        )

    async def embed[T](
        self,
        params: EmbedParams[T],
    ) -> Result[AiEmbeddingResult, AiError]:
        default_node = self.route.nodes[0]
        return await self.run_node(default_node, lambda service: service.embed(params))
