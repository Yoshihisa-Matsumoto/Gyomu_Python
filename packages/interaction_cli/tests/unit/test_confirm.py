import pytest
from gyomu_interaction_cli.confirm import confirm_or_cancel
from pytest_mock import MockerFixture


class TestConfirmOrCancel:
    def test_returns_true_when_confirmed(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        confirm = mocker.patch(
            "gyomu_interaction_cli.confirm.confirm",
        )
        confirm.return_value.ask.return_value = True

        # Act
        result = confirm_or_cancel()

        # Assert
        assert result is True
        confirm.assert_called_once_with("Confirm?")
        confirm.return_value.ask.assert_called_once()

    def test_returns_false_when_cancelled(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        confirm = mocker.patch(
            "gyomu_interaction_cli.confirm.confirm",
        )
        confirm.return_value.ask.return_value = False

        # Act
        result = confirm_or_cancel()

        # Assert
        assert result is False
        confirm.return_value.ask.assert_called_once()

    def test_returns_false_when_selection_is_cancelled(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        confirm = mocker.patch(
            "gyomu_interaction_cli.confirm.confirm",
        )
        confirm.return_value.ask.return_value = None

        # Act
        result = confirm_or_cancel()

        # Assert
        assert result is False
        confirm.return_value.ask.assert_called_once()

    @pytest.mark.parametrize(
        "exception",
        [EOFError(), KeyboardInterrupt()],
    )
    def test_returns_false_when_input_is_interrupted(
        self,
        mocker: MockerFixture,
        exception: EOFError | KeyboardInterrupt,
    ) -> None:
        # Arrange
        confirm = mocker.patch(
            "gyomu_interaction_cli.confirm.confirm",
        )
        confirm.return_value.ask.side_effect = exception

        # Act
        result = confirm_or_cancel()

        # Assert
        assert result is False
        confirm.return_value.ask.assert_called_once()
