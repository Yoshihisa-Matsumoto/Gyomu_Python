from dataclasses import dataclass

from gyomu_schema.option.retry import RetryObserver

from gyomu_ai.error.route import RoutingError
from gyomu_ai.execution.observer import register_retry_observer
from gyomu_ai.provider.pydantic_ai.routing import (
    ModelRoute,
    ModelRouteId,
    ModelRoutes,
    ModelRouteTableId,
)


@dataclass
class __ModelRoutesTables:
    """Internal class to store model routes tables."""

    entries: dict[ModelRouteTableId, ModelRoutes]
    """Dictionary mapping route table IDs to model routes."""


__DEFAULT_ROUTE_TABLE_ID = ModelRouteTableId("__default__")
"""Default model route table ID."""


__model_routes_tables: __ModelRoutesTables = __ModelRoutesTables(entries={})
"""Global store for model routes tables."""


def _get_model_route(
    route_id: ModelRouteId,
    route_table_id: ModelRouteTableId | None = None,
) -> ModelRoute:
    """Retrieves a specific model route from the registry.

    Args:
        route_id (ModelRouteId): The model route ID to retrieve.
        route_table_id (ModelRouteTableId | None): Optional route table ID.

    Returns:
        ModelRoute: The requested model route.
    """
    route_table_id__for_key = (
        route_table_id if route_table_id is not None else __DEFAULT_ROUTE_TABLE_ID
    )
    if route_table_id__for_key not in __model_routes_tables.entries:
        raise RoutingError(
            "Routing Table Not Found", route_id=None, route_table_id=route_table_id
        )

    routes = __model_routes_tables.entries[route_table_id__for_key]
    if route_id not in routes.routes:
        raise RoutingError(
            "Routing Information Not Found",
            route_id=route_id,
            route_table_id=route_table_id,
        )

    return routes.routes[route_id]


def register_model_routes(
    routes: ModelRoutes, route_table_id: ModelRouteTableId | None = None
) -> None:
    """Registers model routes for a given route table ID.

    Args:
        routes (ModelRoutes): The model routes to register.
        route_table_id (ModelRouteTableId | None): Optional route table ID.
    """
    route_table_id__for_key = (
        route_table_id if route_table_id is not None else __DEFAULT_ROUTE_TABLE_ID
    )
    if route_table_id__for_key in __model_routes_tables.entries:
        raise RoutingError(
            message="Route Table ID is already registered",
            route_table_id=route_table_id,
            route_id=None,
        )

    __model_routes_tables.entries[route_table_id__for_key] = routes


@dataclass(frozen=True)
class AiConfiguration:
    """Configuration container for AI model routes and retry observers."""

    model_routes: ModelRoutes
    """Model routes configuration."""

    retry_observer: RetryObserver | None = None
    """Optional retry observer."""


def initialize_ai(config: AiConfiguration) -> None:
    """Initializes AI configuration by registering routes and retry observers.

    Args:
        config (AiConfiguration): The AI configuration to initialize with.
    """
    register_model_routes(config.model_routes)

    if config.retry_observer is not None:
        register_retry_observer(config.retry_observer)
