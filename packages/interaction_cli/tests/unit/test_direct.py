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
from pytest_mock import MockerFixture
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
    def test_accepts_valid_input_after_confirmation(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        text = mocker.patch("gyomu_interaction_cli.direct.text")
        text.return_value.ask.return_value = "hello"
        confirm = mocker.patch(
            "gyomu_interaction_cli.direct.confirm_or_cancel",
            return_value=True,
        )

        # Act
        result = execute_direct_interaction(
            request=create_direct_request(),
        )

        # Assert
        assert result == Success(InteractionAccepted("hello"))
        text.assert_called_once_with("Enter a value\n>")
        text.return_value.ask.assert_called_once()
        confirm.assert_called_once_with()

    def test_retries_after_validation_error_then_confirms(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        text = mocker.patch("gyomu_interaction_cli.direct.text")
        text.return_value.ask.side_effect = ["invalid", "hello"]
        confirm = mocker.patch(
            "gyomu_interaction_cli.direct.confirm_or_cancel",
            return_value=True,
        )
        print_mock = mocker.patch("gyomu_interaction_cli.direct.print")

        # Act
        result = execute_direct_interaction(
            request=create_direct_request(),
        )

        # Assert
        assert result == Success(InteractionAccepted("hello"))
        assert text.return_value.ask.call_count == 2
        confirm.assert_called_once_with()
        print_mock.assert_called_once()
        assert "Invalid input:" in print_mock.call_args.args[0]
        assert "Invalid value." in print_mock.call_args.args[0]

    def test_cancels_when_text_input_is_cancelled(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        text = mocker.patch("gyomu_interaction_cli.direct.text")
        text.return_value.ask.return_value = None
        confirm = mocker.patch(
            "gyomu_interaction_cli.direct.confirm_or_cancel",
        )

        # Act
        result = execute_direct_interaction(
            request=create_direct_request(),
        )

        # Assert
        assert result == Success(InteractionCancelled())
        confirm.assert_not_called()

    def test_cancels_when_confirmation_is_declined(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        text = mocker.patch("gyomu_interaction_cli.direct.text")
        text.return_value.ask.return_value = "hello"
        mocker.patch(
            "gyomu_interaction_cli.direct.confirm_or_cancel",
            return_value=False,
        )

        # Act
        result = execute_direct_interaction(
            request=create_direct_request(),
        )

        # Assert
        assert result == Success(InteractionCancelled())

    @pytest.mark.parametrize(
        "exception",
        [EOFError(), KeyboardInterrupt()],
    )
    def test_cancels_when_text_input_is_interrupted(
        self,
        mocker: MockerFixture,
        exception: EOFError | KeyboardInterrupt,
    ) -> None:
        # Arrange
        text = mocker.patch("gyomu_interaction_cli.direct.text")
        text.return_value.ask.side_effect = exception
        confirm = mocker.patch(
            "gyomu_interaction_cli.direct.confirm_or_cancel",
        )

        # Act / Assert
        with pytest.raises(type(exception)):
            execute_direct_interaction(
                request=create_direct_request(),
            )

        confirm.assert_not_called()
