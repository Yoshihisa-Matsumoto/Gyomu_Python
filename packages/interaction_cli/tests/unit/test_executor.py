from io import StringIO
from unittest.mock import Mock

from gyomu_interaction_cli.executor import CliInteractionExecutor
from gyomu_schema.error.validation import ValidationError
from gyomu_schema.schemas.interaction.request import (
    InteractionDirectRequest,
    InteractionRequest,
)
from gyomu_schema.schemas.interaction.result import (
    InteractionAccepted,
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


def create_direct_request() -> InteractionRequest[str, None, str]:
    return InteractionDirectRequest(
        instruction="Enter a value",
        context=None,
        codec=StringCodec(),
    )


class TestCliInteractionExecutor:
    def test_accepts_valid_direct_input(self) -> None:
        input_func = Mock(return_value="hello")
        output = StringIO()
        executor = CliInteractionExecutor(
            input_func=input_func,
            output=output,
        )

        result = executor.execute(create_direct_request())

        assert result == Success(InteractionAccepted("hello"))
        assert input_func.call_count == 1
        assert output.getvalue() == ""
