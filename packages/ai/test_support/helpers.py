from collections.abc import Callable
from pathlib import Path
from unittest.mock import MagicMock

from gyomu_ai.execution.context import AiModelContext
from gyomu_ai.model.ai_model import BucketId
from gyomu_ai.provider.pydantic_ai.ai_model import (
    PydanticAiEmbedderDefinition,
    PydanticAiModelDefinition,
    PydanticAiModelRegistry,
)
from gyomu_ai.provider.pydantic_ai.google import (
    create_default_pydantic_ai_model_registry,
)
from gyomu_ai.provider.pydantic_ai.route_registry import AiConfiguration, initialize_ai
from gyomu_ai.provider.pydantic_ai.routing import (
    ModelRoute,
    ModelRouteId,
    ModelRoutes,
    RouteNode,
)
from gyomu_schema.option.retry import RetryObserver
from pydantic_ai import Embedder
from pydantic_ai.models import Model


def register_test_google_routing(
    project_dot_env: Path,
    route_id_list: list[ModelRouteId],
    retry_observer: RetryObserver | None = None,
):
    route: RouteNode = RouteNode(
        registry=create_default_pydantic_ai_model_registry(project_dot_env)
    )
    routes: dict[ModelRouteId, ModelRoute] = {}
    for route_id in route_id_list:
        routes[route_id] = ModelRoute((route,))
    initialize_ai(
        AiConfiguration(
            model_routes=ModelRoutes(routes=routes), retry_observer=retry_observer
        )
    )


def create_pydantic_ai_model_definition(
    create_model: Callable[[AiModelContext | None], Model] = lambda _: MagicMock(
        spec=Model
    ),
    bucket_id: BucketId = BucketId("test-model"),
) -> PydanticAiModelDefinition:
    return PydanticAiModelDefinition(
        create_model=create_model,
        bucket_id=bucket_id,
    )


def create_pydantic_ai_embedder_definition(
    create_embedder: Callable[[AiModelContext | None], Embedder] = lambda _: MagicMock(
        spec=Embedder
    ),
    bucket_id: BucketId = BucketId("test-embedding"),
) -> PydanticAiEmbedderDefinition:
    return PydanticAiEmbedderDefinition(
        create_embedder=create_embedder,
        bucket_id=bucket_id,
    )


def create_pydantic_ai_model_registry(
    fast: PydanticAiModelDefinition = create_pydantic_ai_model_definition(),
    smart: PydanticAiModelDefinition = create_pydantic_ai_model_definition(),
    reasoning: PydanticAiModelDefinition = create_pydantic_ai_model_definition(),
    vision: PydanticAiModelDefinition = create_pydantic_ai_model_definition(),
    embedding: PydanticAiEmbedderDefinition = create_pydantic_ai_embedder_definition(),
) -> PydanticAiModelRegistry:
    return PydanticAiModelRegistry(
        fast=fast,
        smart=smart,
        reasoning=reasoning,
        vision=vision,
        embedding=embedding,
    )
