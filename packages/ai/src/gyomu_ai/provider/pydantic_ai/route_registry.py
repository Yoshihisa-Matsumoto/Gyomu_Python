from dataclasses import dataclass

from gyomu_ai.error.route import RoutingError
from gyomu_ai.execution.observer import register_retry_observer
from gyomu_ai.provider.pydantic_ai.routing import (
    ModelRoute,
    ModelRouteId,
    ModelRoutes,
    ModelRouteTableId,
)
from gyomu_schema.option.retry import RetryObserver


@dataclass
class __ModelRoutesTables:
    entries: dict[ModelRouteTableId, ModelRoutes]


__DEFAULT_ROUTE_TABLE_ID = ModelRouteTableId("__default__")

__model_routes_tables: __ModelRoutesTables = __ModelRoutesTables(entries={})


def _get_model_route(
    route_id: ModelRouteId,
    route_table_id: ModelRouteTableId | None = None,
) -> ModelRoute:
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
    model_routes: ModelRoutes
    retry_observer: RetryObserver | None = None


def initialize_ai(config: AiConfiguration) -> None:
    register_model_routes(config.model_routes)

    if config.retry_observer is not None:
        register_retry_observer(config.retry_observer)
