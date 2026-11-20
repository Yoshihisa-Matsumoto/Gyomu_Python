from types import SimpleNamespace
from typing import cast
from unittest.mock import Mock

import pytest
from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.error.validation import ValidationError
from gyomu_schema.protocols.interaction import InteractionExecutor
from gyomu_schema.schemas.config.test.model_defaults import (
    LiteralParameter,
)
from gyomu_schema.schemas.interaction.request import InputMode, InteractionDirectRequest
from gyomu_schema.schemas.interaction.result import (
    InteractionAccepted,
    InteractionCancelled,
)
from gyomu_test.helper.defaults.requirements import (
    MissingParameterDefault,
    ResolvedParameterDefault,
)
from gyomu_workflow.test.helpers._internal.direct import (
    PrimitiveValueCodec,
    _build_direct_interaction_request,
    define_direct_parameter,
)
from gyomu_workflow.test.helpers.update import (
    DefaultTypeParameterContext,
)
from returns.result import Failure, Success

from packages.python_analysis.test_support.helpers import (
    create_primitive_type,
)
from packages.test.test_support.helpers import (
    create_missing_parameter_default,
)


class TestBuildInteractionRequest:
    def test_supported_primitive_type_returns_interaction_request(self) -> None:
        parameter = create_missing_parameter_default(
            missing_types=(create_primitive_type(primitive_type="str"),)
        )
        context = cast(
            DefaultTypeParameterContext,
            SimpleNamespace(parameter=parameter),
        )

        result = _build_direct_interaction_request(parameter_context=context)

        assert isinstance(result, Success)
        request = result.unwrap()

        assert isinstance(request, InteractionDirectRequest)
        assert request.instruction == "Please define your type parameter for "
        assert request.input_mode == InputMode.DIRECT
        assert request.context is context
        assert isinstance(request.codec, PrimitiveValueCodec)
        assert request.initial_value is None

    # def test_unsupported_type_returns_failure(self) -> None:
    #     parameter = create_missing_parameter_default(
    #         missing_types=(create_primitive_type(primitive_type="complex"),)
    #     )
    #     context = cast(
    #         DefaultTypeParameterContext,
    #         SimpleNamespace(parameter=parameter),
    #     )

    #     result = _build_interaction_request(parameter_context=context)

    #     assert isinstance(result, Failure)
    #     error = result.failure()

    #     assert isinstance(error, GyomuError)
    #     assert error.reason == "out_of_bounds"


class TestPrimitiveValueCodec:
    @pytest.mark.parametrize(
        ("primitive_type", "raw_input", "expected"),
        [
            ("str", "hello", "hello"),
            ("int", "42", 42),
            ("bool", "true", True),
            ("bool", "false", False),
            ("float", "3.14", 3.14),
        ],
    )
    def test_parse_supported_primitive_value(
        self,
        primitive_type: str,
        raw_input: str,
        expected: str | int | bool | float,
    ) -> None:
        parameter: MissingParameterDefault = create_missing_parameter_default(
            missing_types=(create_primitive_type(primitive_type=primitive_type),)
        )
        context = cast(
            DefaultTypeParameterContext,
            SimpleNamespace(parameter=parameter),
        )

        result = PrimitiveValueCodec().parse(raw_input=raw_input, context=context)

        assert isinstance(result, Success)
        assert result.unwrap() == LiteralParameter(value=expected)

    @pytest.mark.parametrize(
        ("raw_input", "expected"),
        [
            (" TRUE ", True),
            ("False", False),
        ],
    )
    def test_parse_bool_ignores_case_and_surrounding_whitespace(
        self,
        raw_input: str,
        expected: bool,
    ) -> None:
        parameter = create_missing_parameter_default(
            missing_types=(create_primitive_type(primitive_type="bool"),)
        )
        context = cast(
            DefaultTypeParameterContext,
            SimpleNamespace(parameter=parameter),
        )

        result = PrimitiveValueCodec().parse(raw_input=raw_input, context=context)

        assert isinstance(result, Success)
        assert result.unwrap() == LiteralParameter(value=expected)

    @pytest.mark.parametrize(
        ("primitive_type", "raw_input"),
        [
            ("int", "not-an-int"),
            ("float", "not-a-float"),
            ("bool", "yes"),
        ],
    )
    def test_parse_invalid_input_returns_failure(
        self,
        primitive_type: str,
        raw_input: str,
    ) -> None:
        parameter = create_missing_parameter_default(
            missing_types=(create_primitive_type(primitive_type=primitive_type),)
        )
        context = cast(
            DefaultTypeParameterContext,
            SimpleNamespace(parameter=parameter),
        )

        result = PrimitiveValueCodec().parse(raw_input=raw_input, context=context)

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), ValidationError)

    def test_parse_unsupported_type_returns_failure(self) -> None:
        parameter = create_missing_parameter_default(
            missing_types=(create_primitive_type(primitive_type="complex"),)
        )
        context = cast(
            DefaultTypeParameterContext,
            SimpleNamespace(parameter=parameter),
        )

        result = PrimitiveValueCodec().parse(raw_input="1+2j", context=context)

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), ValidationError)
        assert "Unsupported Type" in result.failure().message


class TestDefineDirectParameter:
    def _create_context(
        self, primitive_type: str = "str"
    ) -> DefaultTypeParameterContext:
        parameter = create_missing_parameter_default(
            missing_types=(create_primitive_type(primitive_type=primitive_type),)
        )
        return cast(
            DefaultTypeParameterContext,
            SimpleNamespace(parameter=parameter),
        )

    def test_accepted_returns_resolved_parameter_default(self) -> None:
        context = self._create_context()
        executor = Mock(spec=InteractionExecutor)
        value = LiteralParameter(value="hello")
        executor.execute.return_value = Success(InteractionAccepted(value=value))

        result = define_direct_parameter(
            parameter_context=context,
            interaction=executor,
        )

        assert isinstance(result, Success)
        resolved = result.unwrap()
        assert isinstance(resolved, ResolvedParameterDefault)
        assert resolved.parameter is context.parameter.parameter
        assert resolved.default == value

        executor.execute.assert_called_once()
        request = executor.execute.call_args.kwargs["request"]
        assert isinstance(request, InteractionDirectRequest)
        assert request.context is context
        assert isinstance(request.codec, PrimitiveValueCodec)

    def test_cancelled_returns_failure(self) -> None:
        context = self._create_context()
        executor = Mock(spec=InteractionExecutor)
        executor.execute.return_value = Success(InteractionCancelled())

        result = define_direct_parameter(
            parameter_context=context,
            interaction=executor,
        )

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), GyomuError)
        assert result.failure().reason == "external_failure"
        executor.execute.assert_called_once()

    def test_executor_failure_is_propagated(self) -> None:
        context = self._create_context()
        executor = Mock(spec=InteractionExecutor)
        error = GyomuError(
            "interaction failed",
            operation="test",
            domain="test",
            reason="external_failure",
        )
        executor.execute.return_value = Failure(error)

        result = define_direct_parameter(
            parameter_context=context,
            interaction=executor,
        )

        assert isinstance(result, Failure)
        assert result.failure() is error
        executor.execute.assert_called_once()

    # def test_unsupported_type_does_not_call_executor(self) -> None:
    #     context = self._create_context(primitive_type="complex")
    #     executor = Mock(spec=InteractionExecutor)

    #     result = _define_parameter(
    #         parameter_context=context,
    #         interaction=executor,
    #     )

    #     assert isinstance(result, Failure)
    #     assert isinstance(result.failure(), GyomuError)
    #     assert result.failure().reason == "out_of_bounds"
    #     executor.execute.assert_not_called()
