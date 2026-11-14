from io import StringIO
from unittest.mock import Mock

import pytest
from gyomu_interaction_cli.direct import execute_direct_interaction
from gyomu_schema.error.validation import ValidationError
from gyomu_schema.schemas.interaction.request import (
    InputMode,
    InteractionDirectRequest,
)
from gyomu_schema.schemas.interaction.result import (
    InteractionAccepted,
    InteractionCancelled,
    InteractionRejected,
)
from returns.result import Failure, Success


class StringCodec:
    def parse(
        self,
        raw_input: str,
        context: None,
    ) -> Success[str] | Failure[ValidationError]:
        if raw_input == "invalid":
            return Failure(ValidationError("Invalid value."))

        return Success(raw_input)


def create_direct_request(
    *,
    input_mode: InputMode = InputMode.DIRECT,
) -> InteractionDirectRequest[str, None, str]:
    return InteractionDirectRequest(
        instruction="Enter a value",
        context=None,
        codec=StringCodec(),
    )


class TestExecuteDirectInteraction:
    def test_accepts_valid_input(self) -> None:
        input_func = Mock(return_value="hello")
        output = StringIO()

        result = execute_direct_interaction(
            request=create_direct_request(), input_func=input_func, output=output
        )

        assert result == Success(InteractionAccepted("hello"))
        assert input_func.call_count == 1
        assert output.getvalue() == ""

    def test_retries_after_validation_error(self) -> None:
        input_func = Mock(side_effect=["invalid", "hello"])
        output = StringIO()

        result = execute_direct_interaction(
            request=create_direct_request(), input_func=input_func, output=output
        )
        assert result == Success(InteractionAccepted("hello"))
        assert input_func.call_count == 2
        assert "Invalid input:" in output.getvalue()
        assert "Invalid value." in output.getvalue()

    @pytest.mark.parametrize(
        ("raw_input", "expected"),
        [
            (":cancel", InteractionCancelled()),
            (":reject", InteractionRejected()),
        ],
    )
    def test_handles_control_commands(
        self,
        raw_input: str,
        expected: InteractionCancelled | InteractionRejected,
    ) -> None:
        input_func = Mock(return_value=raw_input)
        output = StringIO()
        result = execute_direct_interaction(
            request=create_direct_request(), input_func=input_func, output=output
        )

        assert result == Success(expected)
        assert input_func.call_count == 1
        assert output.getvalue() == ""

    @pytest.mark.parametrize(
        "exception",
        [EOFError(), KeyboardInterrupt()],
    )
    def test_cancels_when_input_is_interrupted(
        self,
        exception: EOFError | KeyboardInterrupt,
    ) -> None:
        input_func = Mock(side_effect=exception)
        output = StringIO()
        result = execute_direct_interaction(
            request=create_direct_request(), input_func=input_func, output=output
        )

        assert result == Success(InteractionCancelled())
        assert output.getvalue() == ""

    # def test_returns_failure_for_unsupported_input_mode(self) -> None:
    #     input_func = Mock()
    #     output = StringIO()
    #     result = execute_direct_interaction(
    #         request=create_direct_request(input_mode=InputMode.DOCUMENT),
    #         input_func=input_func,
    #         output=output,
    #     )

    #     assert isinstance(result, Failure)
    #     assert isinstance(result.failure(), GyomuError)
    #     input_func.assert_not_called()
    #     assert output.getvalue() == ""
