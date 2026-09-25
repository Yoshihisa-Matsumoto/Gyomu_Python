from unittest.mock import MagicMock

import pytest
from gyomu_ai.error.route import RoutingError
from gyomu_ai.execution import observer as observer_module
from gyomu_ai.provider.pydantic_ai import route_registry
from gyomu_ai.provider.pydantic_ai.ai_model import PydanticAiModelRegistry
from gyomu_ai.provider.pydantic_ai.route_registry import (
    AiConfiguration,
    _get_model_route,
    initialize_ai,
    register_model_routes,
)
from gyomu_ai.provider.pydantic_ai.routing import (
    ModelRoute,
    ModelRouteId,
    ModelRoutes,
    ModelRouteTableId,
    RouteNode,
)
from gyomu_schema.option.retry import RetryObserver


@pytest.fixture(autouse=True)
def reset_route_registry() -> None:
    route_registry.__model_routes_tables.entries.clear()
    observer_module.__OBSERVER = None


def create_model_route() -> ModelRoute:
    registry = MagicMock(spec=PydanticAiModelRegistry)
    return ModelRoute(nodes=(RouteNode(registry=registry),))


def create_model_routes(
    route_id: ModelRouteId,
) -> tuple[ModelRoutes, ModelRoute]:
    route = create_model_route()
    return ModelRoutes(routes={route_id: route}), route


class TestGetModelRoute:
    def test_get_default_route(self) -> None:
        route_id = ModelRouteId("test-route")
        routes, expected = create_model_routes(route_id)

        register_model_routes(routes)

        actual = _get_model_route(route_id)

        assert actual is expected

    def test_get_route_from_named_table(self) -> None:
        route_id = ModelRouteId("test-route")
        table_id = ModelRouteTableId("test-table")
        routes, expected = create_model_routes(route_id)

        register_model_routes(routes, table_id)

        actual = _get_model_route(route_id, table_id)

        assert actual is expected

    def test_raise_when_route_table_not_found(self) -> None:
        route_id = ModelRouteId("test-route")

        with pytest.raises(RoutingError) as exc_info:
            _get_model_route(route_id)

        assert exc_info.value.message == "Routing Table Not Found"
        assert exc_info.value.route_id is None
        assert exc_info.value.table_id is None

    def test_raise_when_named_route_table_not_found(self) -> None:
        route_id = ModelRouteId("test-route")
        table_id = ModelRouteTableId("test-table")

        with pytest.raises(RoutingError) as exc_info:
            _get_model_route(route_id, table_id)

        assert exc_info.value.message == "Routing Table Not Found"
        assert exc_info.value.route_id is None
        assert exc_info.value.table_id == table_id

    def test_raise_when_route_not_found(self) -> None:
        registered_route_id = ModelRouteId("registered-route")
        requested_route_id = ModelRouteId("requested-route")
        routes, _ = create_model_routes(registered_route_id)

        register_model_routes(routes)

        with pytest.raises(RoutingError) as exc_info:
            _get_model_route(requested_route_id)

        assert exc_info.value.message == "Routing Information Not Found"
        assert exc_info.value.route_id == requested_route_id
        assert exc_info.value.table_id is None

    def test_raise_when_route_not_found_in_named_table(self) -> None:
        registered_route_id = ModelRouteId("registered-route")
        requested_route_id = ModelRouteId("requested-route")
        table_id = ModelRouteTableId("test-table")
        routes, _ = create_model_routes(registered_route_id)

        register_model_routes(routes, table_id)

        with pytest.raises(RoutingError) as exc_info:
            _get_model_route(requested_route_id, table_id)

        assert exc_info.value.message == "Routing Information Not Found"
        assert exc_info.value.route_id == requested_route_id
        assert exc_info.value.table_id == table_id


class TestRegisterModelRoutes:
    def test_register_default_route_table(self) -> None:
        route_id = ModelRouteId("test-route")
        routes, expected = create_model_routes(route_id)

        register_model_routes(routes)

        assert _get_model_route(route_id) is expected

    def test_register_named_route_table(self) -> None:
        route_id = ModelRouteId("test-route")
        table_id = ModelRouteTableId("test-table")
        routes, expected = create_model_routes(route_id)

        register_model_routes(routes, table_id)

        assert _get_model_route(route_id, table_id) is expected

    def test_raise_when_default_route_table_already_registered(self) -> None:
        routes, _ = create_model_routes(ModelRouteId("test-route"))

        register_model_routes(routes)

        with pytest.raises(RoutingError) as exc_info:
            register_model_routes(routes)

        assert exc_info.value.message == "Route Table ID is already registered"
        assert exc_info.value.route_id is None
        assert exc_info.value.table_id is None

    def test_raise_when_named_route_table_already_registered(self) -> None:
        table_id = ModelRouteTableId("test-table")
        routes, _ = create_model_routes(ModelRouteId("test-route"))

        register_model_routes(routes, table_id)

        with pytest.raises(RoutingError) as exc_info:
            register_model_routes(routes, table_id)

        assert exc_info.value.message == "Route Table ID is already registered"
        assert exc_info.value.route_id is None
        assert exc_info.value.table_id == table_id


class TestInitializeAi:
    def test_register_model_routes(self) -> None:
        route_id = ModelRouteId("test-route")
        routes, expected = create_model_routes(route_id)

        initialize_ai(
            AiConfiguration(
                model_routes=routes,
            )
        )

        assert _get_model_route(route_id) is expected

    def test_register_retry_observer(self) -> None:
        routes, _ = create_model_routes(ModelRouteId("test-route"))
        observer = MagicMock(spec=RetryObserver)

        initialize_ai(
            AiConfiguration(
                model_routes=routes,
                retry_observer=observer,
            )
        )

        assert observer_module._get_retry_observer() is observer

    def test_do_not_register_retry_observer_when_not_specified(self) -> None:
        routes, _ = create_model_routes(ModelRouteId("test-route"))

        initialize_ai(
            AiConfiguration(
                model_routes=routes,
            )
        )

        assert observer_module._get_retry_observer() is None

    def test_raise_when_retry_observer_already_registered(self) -> None:
        routes, _ = create_model_routes(ModelRouteId("test-route"))
        first_observer = MagicMock(spec=RetryObserver)
        second_observer = MagicMock(spec=RetryObserver)

        observer_module.register_retry_observer(first_observer)

        with pytest.raises(ValueError, match="RetryObserver is already registered"):
            initialize_ai(
                AiConfiguration(
                    model_routes=routes,
                    retry_observer=second_observer,
                )
            )

        assert observer_module._get_retry_observer() is first_observer
