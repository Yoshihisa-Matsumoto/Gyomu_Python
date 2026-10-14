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
    create_model: Callable[[AiModelContext | None], Model] | None = None,
    *,
    bucket_id: BucketId = BucketId("test-model"),  # noqa: B008
) -> PydanticAiModelDefinition:
    return PydanticAiModelDefinition(
        create_model=(
            create_model
            if create_model is not None
            else lambda _: MagicMock(spec=Model)
        ),
        bucket_id=bucket_id,
    )


def create_pydantic_ai_embedder_definition(
    create_embedder: Callable[[AiModelContext | None], Embedder] | None = None,
    *,
    bucket_id: BucketId = BucketId("test-embedding"),  # noqa: B008
) -> PydanticAiEmbedderDefinition:
    return PydanticAiEmbedderDefinition(
        create_embedder=(
            create_embedder
            if create_embedder is not None
            else lambda _: MagicMock(spec=Embedder)
        ),
        bucket_id=bucket_id,
    )


def create_pydantic_ai_model_registry(
    *,
    fast: PydanticAiModelDefinition | None = None,
    smart: PydanticAiModelDefinition | None = None,
    reasoning: PydanticAiModelDefinition | None = None,
    vision: PydanticAiModelDefinition | None = None,
    embedding: PydanticAiEmbedderDefinition | None = None,
) -> PydanticAiModelRegistry:
    return PydanticAiModelRegistry(
        fast=fast if fast is not None else create_pydantic_ai_model_definition(),
        smart=smart if smart is not None else create_pydantic_ai_model_definition(),
        reasoning=(
            reasoning
            if reasoning is not None
            else create_pydantic_ai_model_definition()
        ),
        vision=vision if vision is not None else create_pydantic_ai_model_definition(),
        embedding=(
            embedding
            if embedding is not None
            else create_pydantic_ai_embedder_definition()
        ),
    )
