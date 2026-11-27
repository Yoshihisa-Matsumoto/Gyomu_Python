from unittest.mock import Mock

from gyomu_schema.schemas.interaction.request import (
    InteractionSelectRequest,
    SelectionOption,
)
from gyomu_schema.schemas.interaction.result import (
    InteractionAccepted,
    InteractionCancelled,
)
from gyomu_workflow.interaction.confirm import (
    SimpleConfirmationSelectionProvider,
    _build_simple_confirm_selection_request,
    simple_confirm,
)
from returns.result import Failure, Success

from packages.schema.test_support.helpers import create_gyomu_error


class TestSimpleConfirmationSelectionProvider:
    def test_creates_yes_and_no_selections(self) -> None:
        # Arrange
        provider = SimpleConfirmationSelectionProvider()

        # Act
        result = provider.create_selections(context=None)

        # Assert
        assert result == Success(
            (
                SelectionOption[bool](label="Yes", value=True),
                SelectionOption[bool](label="No", value=False),
            )
        )


class TestBuildSimpleConfirmSelectionRequest:
    def test_builds_selection_request(self) -> None:
        # Arrange
        instruction = "Continue?"
        initial_value = True

        # Act
        result = _build_simple_confirm_selection_request(
            instructuion=instruction,
            initial_value=initial_value,
        )

        # Assert
        assert isinstance(result, InteractionSelectRequest)
        assert result.instruction == instruction
        assert result.context is None
        assert isinstance(
            result.selection_provider, SimpleConfirmationSelectionProvider
        )
        assert result.initial_value is initial_value


class TestSimpleConfirm:
    def test_returns_failure_when_interaction_fails(
        self,
    ) -> None:
        # Arrange
        instruction = "Continue?"
        error = create_gyomu_error()
        interaction = Mock()
        interaction.execute.return_value = Failure(error)

        # Act
        result = simple_confirm(
            instruction=instruction,
            interaction=interaction,
            initial_value=False,
        )

        # Assert
        assert isinstance(result, Failure)
        assert result.failure() == error
        interaction.execute.assert_called_once()

    def test_returns_success_none_when_interaction_is_cancelled(self) -> None:
        # Arrange
        interaction = Mock()
        interaction.execute.return_value = Success(InteractionCancelled())

        # Act
        result = simple_confirm(
            instruction="Continue?",
            interaction=interaction,
            initial_value=False,
        )

        # Assert
        assert result == Success(None)
        interaction.execute.assert_called_once()

    def test_returns_selected_value_when_interaction_succeeds(self) -> None:
        # Arrange
        interaction = Mock()
        interaction.execute.return_value = Success(InteractionAccepted(value=True))

        # Act
        result = simple_confirm(
            instruction="Continue?",
            interaction=interaction,
            initial_value=False,
        )

        # Assert
        assert result == Success(True)
        interaction.execute.assert_called_once()

    def test_returns_false_when_no_is_selected(self) -> None:
        # Arrange
        interaction = Mock()
        interaction.execute.return_value = Success(InteractionAccepted(value=False))

        # Act
        result = simple_confirm(
            instruction="Continue?",
            interaction=interaction,
            initial_value=True,
        )

        # Assert
        assert result == Success(False)
        interaction.execute.assert_called_once()

    def test_passes_confirmation_request_to_interaction(self) -> None:
        # Arrange
        instruction = "Continue?"
        initial_value = False
        interaction = Mock()
        interaction.execute.return_value = Success(InteractionAccepted(value=True))

        # Act
        result = simple_confirm(
            instruction=instruction,
            interaction=interaction,
            initial_value=initial_value,
        )

        # Assert
        assert result == Success(True)
        interaction.execute.assert_called_once()
        request = interaction.execute.call_args.kwargs["request"]
        assert isinstance(request, InteractionSelectRequest)
        assert request.instruction == instruction
        assert request.initial_value is initial_value
