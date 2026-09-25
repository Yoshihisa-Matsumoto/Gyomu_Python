from pathlib import Path

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
