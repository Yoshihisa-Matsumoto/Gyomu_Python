from collections.abc import Awaitable, Callable
from unittest.mock import AsyncMock, MagicMock

import pytest
from gyomu_ai.provider.pydantic_ai import route_service as route_service_module
from gyomu_ai.provider.pydantic_ai.execution import PydanticAiModelExecution
from gyomu_ai.provider.pydantic_ai.routing import (
    ModelRoute,
    ModelRouteId,
    RouteNode,
)
from gyomu_schema.error.ai import (
    AiError,
    AiFailResolution,
    AiFallbackResolution,
)
from returns.result import Failure, Result, Success


@pytest.fixture
def route_node() -> RouteNode:
    return RouteNode(
        registry=MagicMock(),
    )


@pytest.fixture
def second_route_node() -> RouteNode:
    return RouteNode(
        registry=MagicMock(),
    )


@pytest.fixture
def execution(
    mocker,
    route_node: RouteNode,
) -> route_service_module.PydanticAiRoutingExecution:
    route = ModelRoute(nodes=(route_node,))

    mocker.patch.object(
        route_service_module,
        "_get_model_route",
        return_value=route,
    )

    return route_service_module.PydanticAiRoutingExecution(
        route_id=ModelRouteId("test-route"),
    )


class TestPydanticAiRoutingExecution:
    async def test_run_node(
        self,
        mocker,
        route_node: RouteNode,
    ) -> None:
        execution = route_service_module.PydanticAiRoutingExecution.__new__(
            route_service_module.PydanticAiRoutingExecution
        )

        model_execution = MagicMock(spec=PydanticAiModelExecution)

        model_execution_constructor = mocker.patch.object(
            route_service_module,
            "PydanticAiModelExecution",
            return_value=model_execution,
        )

        expected = Success("success")

        async def execute(
            service: PydanticAiModelExecution,
        ) -> Result[str, AiError]:
            assert service is model_execution
            return expected

        actual = await execution.run_node(route_node, execute)

        assert actual is expected

        model_execution_constructor.assert_called_once_with(
            route_node.registry,
            retry_option=route_node.retry_option,
        )

    async def test_run_with_model_route_returns_success(
        self,
        mocker,
        route_node: RouteNode,
    ) -> None:
        execution = route_service_module.PydanticAiRoutingExecution.__new__(
            route_service_module.PydanticAiRoutingExecution
        )
        execution.route = ModelRoute(nodes=(route_node,))

        expected = Success("success")

        execution.run_node = AsyncMock(return_value=expected)

        async def execute(
            service: PydanticAiModelExecution,
        ) -> Result[str, AiError]:
            return expected

        actual = await execution.run_with_model_route(execute)

        assert actual is expected
        execution.run_node.assert_awaited_once_with(
            route_node,
            execute,
        )

    async def test_run_with_model_route_stops_on_non_fallback_error(
        self,
        mocker,
        route_node: RouteNode,
        second_route_node: RouteNode,
    ) -> None:
        execution = route_service_module.PydanticAiRoutingExecution.__new__(
            route_service_module.PydanticAiRoutingExecution
        )
        execution.route = ModelRoute(
            nodes=(route_node, second_route_node),
        )

        error = MagicMock(spec=AiError)
        error.resolution = AiFailResolution()

        execution.run_node = AsyncMock(
            return_value=Failure(error),
        )

        async def execute(
            service: PydanticAiModelExecution,
        ) -> Result[str, AiError]:
            return Failure(error)

        actual = await execution.run_with_model_route(execute)

        assert isinstance(actual, Failure)
        assert actual.failure() is error
        execution.run_node.assert_awaited_once_with(
            route_node,
            execute,
        )

    async def test_run_with_model_route_falls_back_to_next_node(
        self,
        route_node: RouteNode,
        second_route_node: RouteNode,
    ) -> None:
        execution = route_service_module.PydanticAiRoutingExecution.__new__(
            route_service_module.PydanticAiRoutingExecution
        )
        execution.route = ModelRoute(
            nodes=(route_node, second_route_node),
        )

        first_error = MagicMock(spec=AiError)
        first_error.resolution = AiFallbackResolution()

        expected = Success("success")

        execution.run_node = AsyncMock(
            side_effect=[
                Failure(first_error),
                expected,
            ],
        )

        async def execute(
            service: PydanticAiModelExecution,
        ) -> Result[str, AiError]:
            return expected

        actual = await execution.run_with_model_route(execute)

        assert actual is expected
        assert execution.run_node.await_count == 2
        execution.run_node.assert_any_await(route_node, execute)
        execution.run_node.assert_any_await(second_route_node, execute)

    async def test_run_with_model_route_returns_last_error_when_all_nodes_fallback(
        self,
        route_node: RouteNode,
        second_route_node: RouteNode,
    ) -> None:
        execution = route_service_module.PydanticAiRoutingExecution.__new__(
            route_service_module.PydanticAiRoutingExecution
        )
        execution.route = ModelRoute(
            nodes=(route_node, second_route_node),
        )

        first_error = MagicMock(spec=AiError)
        first_error.resolution = AiFallbackResolution()

        last_error = MagicMock(spec=AiError)
        last_error.resolution = AiFallbackResolution()

        execution.run_node = AsyncMock(
            side_effect=[
                Failure(first_error),
                Failure(last_error),
            ],
        )

        async def execute(
            service: PydanticAiModelExecution,
        ) -> Result[str, AiError]:
            return Failure(last_error)

        actual = await execution.run_with_model_route(execute)

        assert isinstance(actual, Failure)
        assert actual.failure() is last_error
        assert execution.run_node.await_count == 2

    async def test_generate_text_delegates_to_model_execution(
        self,
        mocker,
        execution,
    ) -> None:
        conversation = MagicMock()
        params = MagicMock()
        expected = Success("result")

        service = MagicMock(spec=PydanticAiModelExecution)
        service.generate_text = AsyncMock(return_value=expected)

        async def run_with_model_route(
            execute: Callable[
                [PydanticAiModelExecution],
                Awaitable[Result[object, AiError]],
            ],
        ) -> Result[object, AiError]:
            return await execute(service)

        mocker.patch.object(
            execution,
            "run_with_model_route",
            side_effect=run_with_model_route,
        )

        actual = await execution.generate_text(conversation, params)

        assert actual is expected
        service.generate_text.assert_awaited_once_with(conversation, params)

    async def test_stream_text_delegates_to_model_execution(
        self,
        mocker,
        execution,
    ) -> None:
        conversation = MagicMock()
        params = MagicMock()
        expected = Success("result")

        service = MagicMock(spec=PydanticAiModelExecution)
        service.stream_text = AsyncMock(return_value=expected)

        async def execute(
            callback,
        ):
            return await callback(service)

        run_with_model_route = mocker.patch.object(
            execution,
            "run_with_model_route",
            side_effect=execute,
        )

        actual = await execution.stream_text(conversation, params)

        assert actual is expected
        run_with_model_route.assert_called_once()
        service.stream_text.assert_awaited_once_with(conversation, params)

    async def test_generate_object_delegates_to_model_execution(
        self,
        mocker,
        execution,
    ) -> None:
        conversation = MagicMock()
        params = MagicMock()
        expected = Success("result")

        service = MagicMock(spec=PydanticAiModelExecution)
        service.generate_object = AsyncMock(return_value=expected)

        async def execute(
            callback,
        ):
            return await callback(service)

        run_with_model_route = mocker.patch.object(
            execution,
            "run_with_model_route",
            side_effect=execute,
        )

        actual = await execution.generate_object(conversation, params)

        assert actual is expected
        run_with_model_route.assert_called_once()
        service.generate_object.assert_awaited_once_with(conversation, params)

    async def test_embed_uses_first_route_node(
        self,
        mocker,
        route_node: RouteNode,
        second_route_node: RouteNode,
    ) -> None:
        execution = route_service_module.PydanticAiRoutingExecution.__new__(
            route_service_module.PydanticAiRoutingExecution
        )
        execution.route = ModelRoute(
            nodes=(route_node, second_route_node),
        )

        params = MagicMock()
        expected = Success("embedding")

        execution.run_node = AsyncMock(return_value=expected)

        actual = await execution.embed(params)

        assert actual is expected

        execution.run_node.assert_awaited_once()
        assert execution.run_node.await_args is not None
        assert execution.run_node.await_args.args[0] is route_node
