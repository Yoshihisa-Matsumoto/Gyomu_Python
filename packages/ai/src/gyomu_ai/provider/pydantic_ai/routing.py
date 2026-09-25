from collections.abc import Mapping
from dataclasses import dataclass
from typing import NewType

from gyomu_ai.error.route import RoutingError
from gyomu_ai.provider.pydantic_ai.ai_model import PydanticAiModelRegistry

ModelRouteId = NewType("ModelRouteId", str)
ModelRouteTableId = NewType("ModelRouteTableId", str)


@dataclass
class RouteNode:
    registry: PydanticAiModelRegistry
    retry: int


@dataclass
class ModelRoute:
    nodes: tuple[RouteNode, ...]


@dataclass
class ModelRoutes:
    routes: Mapping[ModelRouteId, ModelRoute]


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
