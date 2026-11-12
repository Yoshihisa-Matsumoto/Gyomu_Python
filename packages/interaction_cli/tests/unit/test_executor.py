from io import StringIO
from unittest.mock import Mock

import pytest
from gyomu_interaction_cli.executor import CliInteractionExecutor
from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.error.validation import ValidationError
from gyomu_schema.schemas.interaction.request import (
    InputMode,
    InteractionRequest,
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


def create_request(
    *,
    input_mode: InputMode = InputMode.DIRECT,
) -> InteractionRequest[str, None, str]:
    return InteractionRequest(
        instruction="Enter a value",
        input_mode=input_mode,
        context=None,
        codec=StringCodec(),
    )


class TestCliInteractionExecutor:
    def test_accepts_valid_input(self) -> None:
        input_func = Mock(return_value="hello")
        output = StringIO()
        executor = CliInteractionExecutor(
            input_func=input_func,
            output=output,
        )

        result = executor.execute(create_request())

        assert result == Success(InteractionAccepted("hello"))
        assert input_func.call_count == 1
        assert output.getvalue() == ""

    def test_retries_after_validation_error(self) -> None:
        input_func = Mock(side_effect=["invalid", "hello"])
        output = StringIO()
        executor = CliInteractionExecutor(
            input_func=input_func,
            output=output,
        )

        result = executor.execute(create_request())

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
        executor = CliInteractionExecutor(
            input_func=input_func,
            output=output,
        )

        result = executor.execute(create_request())

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
        executor = CliInteractionExecutor(
            input_func=input_func,
            output=output,
        )

        result = executor.execute(create_request())

        assert result == Success(InteractionCancelled())
        assert output.getvalue() == ""

    def test_returns_failure_for_unsupported_input_mode(self) -> None:
        input_func = Mock()
        output = StringIO()
        executor = CliInteractionExecutor(
            input_func=input_func,
            output=output,
        )

        result = executor.execute(create_request(input_mode=InputMode.DOCUMENT))

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), GyomuError)
        input_func.assert_not_called()
        assert output.getvalue() == ""
