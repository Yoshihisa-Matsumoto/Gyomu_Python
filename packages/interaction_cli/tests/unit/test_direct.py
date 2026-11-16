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
    def test_accepts_valid_input_after_confirmation(self) -> None:
        input_func = Mock(side_effect=["hello", "y"])
        output = StringIO()

        result = execute_direct_interaction(
            request=create_direct_request(),
            input_func=input_func,
            output=output,
        )

        assert result == Success(InteractionAccepted("hello"))
        assert input_func.call_count == 2
        assert output.getvalue() == ""

    def test_retries_after_validation_error_then_confirms(self) -> None:
        input_func = Mock(side_effect=["invalid", "hello", "y"])
        output = StringIO()

        result = execute_direct_interaction(
            request=create_direct_request(),
            input_func=input_func,
            output=output,
        )

        assert result == Success(InteractionAccepted("hello"))
        assert input_func.call_count == 3
        assert "Invalid input:" in output.getvalue()
        assert "Invalid value." in output.getvalue()

    def test_cancels_after_input(self) -> None:
        input_func = Mock(side_effect=["hello", "n"])
        output = StringIO()

        result = execute_direct_interaction(
            request=create_direct_request(),
            input_func=input_func,
            output=output,
        )

        assert result == Success(InteractionCancelled())
        assert input_func.call_count == 2
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
            request=create_direct_request(),
            input_func=input_func,
            output=output,
        )

        assert result == Success(InteractionCancelled())
        assert input_func.call_count == 1
        assert output.getvalue() == ""

    @pytest.mark.parametrize(
        "exception",
        [EOFError(), KeyboardInterrupt()],
    )
    def test_cancels_when_confirmation_is_interrupted(
        self,
        exception: EOFError | KeyboardInterrupt,
    ) -> None:
        input_func = Mock(side_effect=["hello", exception])
        output = StringIO()

        result = execute_direct_interaction(
            request=create_direct_request(),
            input_func=input_func,
            output=output,
        )

        assert result == Success(InteractionCancelled())
        assert input_func.call_count == 2
        assert output.getvalue() == ""
