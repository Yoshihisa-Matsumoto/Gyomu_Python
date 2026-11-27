from gyomu_interaction_cli.select import (
    _selection_to_choice,
    execute_selection_interaction,
)
from gyomu_schema.schemas.interaction.request import (
    InteractionSelectRequest,
    SelectionOption,
)
from gyomu_schema.schemas.interaction.result import (
    InteractionAccepted,
    InteractionCancelled,
)
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.schema.test_support.helpers import create_gyomu_error


class TestSelection_ToChoice:
    def test_checks_matching_initial_value(self) -> None:
        # Arrange
        selection = SelectionOption(
            label="Workspace",
            value="workspace",
        )

        # Act
        choice = _selection_to_choice(
            selection=selection,
            initial_value="workspace",
        )

        # Assert
        assert choice.title == "Workspace"
        assert choice.value == "workspace"
        assert choice.checked is True

    def test_does_not_check_non_matching_initial_value(self) -> None:
        # Arrange
        selection = SelectionOption(
            label="Workspace",
            value="workspace",
        )

        # Act
        choice = _selection_to_choice(
            selection=selection,
            initial_value="project",
        )

        # Assert
        assert choice.title == "Workspace"
        assert choice.value == "workspace"
        assert choice.checked is False

    def test_does_not_check_when_initial_value_is_none(self) -> None:
        # Arrange
        selection = SelectionOption(
            label="Workspace",
            value="workspace",
        )

        # Act
        choice = _selection_to_choice(
            selection=selection,
            initial_value=None,
        )

        # Assert
        assert choice.title == "Workspace"
        assert choice.value == "workspace"
        assert choice.checked is False


class TestExecuteSelectionInteraction:
    def test_returns_selected_value(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        selection = SelectionOption(
            label="Workspace",
            value="workspace",
        )
        selection_provider = mocker.Mock()
        selection_provider.create_selections.return_value = Success((selection,))

        select = mocker.patch(
            "gyomu_interaction_cli.select.select",
        )
        select.return_value.ask.return_value = "workspace"

        request = InteractionSelectRequest[None, None](
            instruction="Select a scope",
            context=None,
            selection_provider=selection_provider,
        )

        # Act
        result = execute_selection_interaction(
            request=request,
        )

        # Assert
        assert isinstance(result, Success)
        interaction_result = result.unwrap()
        assert isinstance(interaction_result, InteractionAccepted)
        assert interaction_result.value == "workspace"
        select.assert_called_once()

    def test_returns_failure_when_selection_creation_fails(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        error = create_gyomu_error()
        selection_provider = mocker.Mock()
        selection_provider.create_selections.return_value = Failure(error)

        request = InteractionSelectRequest(
            instruction="Select a scope",
            context=None,
            selection_provider=selection_provider,
        )

        # Act
        result = execute_selection_interaction(request=request)

        # Assert
        assert isinstance(result, Failure)
        assert result.failure() is error

    def test_returns_failure_when_selections_are_empty(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        selection_provider = mocker.Mock()
        selection_provider.create_selections.return_value = Success(())

        request = InteractionSelectRequest(
            instruction="Select a scope",
            context=None,
            selection_provider=selection_provider,
        )

        # Act
        result = execute_selection_interaction(request=request)

        # Assert
        assert isinstance(result, Failure)
        assert result.failure().message == "fail to initialize selection items"

    def test_returns_cancelled_when_selection_is_cancelled(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        selection = SelectionOption(
            label="Workspace",
            value="workspace",
        )
        selection_provider = mocker.Mock()
        selection_provider.create_selections.return_value = Success((selection,))

        select = mocker.patch(
            "gyomu_interaction_cli.select.select",
        )
        select.return_value.ask.return_value = None

        request = InteractionSelectRequest(
            instruction="Select a scope",
            context=None,
            selection_provider=selection_provider,
        )

        # Act
        result = execute_selection_interaction(request=request)

        # Assert
        assert isinstance(result, Success)
        assert isinstance(result.unwrap(), InteractionCancelled)
        select.return_value.ask.assert_called_once()

    def test_returns_cancelled_when_keyboard_interrupt_occurs(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        selection = SelectionOption(
            label="Workspace",
            value="workspace",
        )
        selection_provider = mocker.Mock()
        selection_provider.create_selections.return_value = Success((selection,))

        select = mocker.patch(
            "gyomu_interaction_cli.select.select",
        )
        select.return_value.ask.side_effect = KeyboardInterrupt

        request = InteractionSelectRequest(
            instruction="Select a scope",
            context=None,
            selection_provider=selection_provider,
        )

        # Act
        result = execute_selection_interaction(request=request)

        # Assert
        assert isinstance(result, Success)
        assert isinstance(result.unwrap(), InteractionCancelled)
        select.return_value.ask.assert_called_once()

    def test_returns_cancelled_when_eof_error_occurs(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        selection = SelectionOption(
            label="Workspace",
            value="workspace",
        )
        selection_provider = mocker.Mock()
        selection_provider.create_selections.return_value = Success((selection,))

        select = mocker.patch(
            "gyomu_interaction_cli.select.select",
        )
        select.return_value.ask.side_effect = EOFError

        request = InteractionSelectRequest(
            instruction="Select a scope",
            context=None,
            selection_provider=selection_provider,
        )

        # Act
        result = execute_selection_interaction(request=request)

        # Assert
        assert isinstance(result, Success)
        assert isinstance(result.unwrap(), InteractionCancelled)
        select.return_value.ask.assert_called_once()

    def test_passes_instruction_and_choices_to_select(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        selections = (
            SelectionOption(label="Workspace", value="workspace"),
            SelectionOption(label="Project", value="project"),
        )
        selection_provider = mocker.Mock()
        selection_provider.create_selections.return_value = Success(selections)

        select = mocker.patch(
            "gyomu_interaction_cli.select.select",
        )
        select.return_value.ask.return_value = "workspace"

        request = InteractionSelectRequest(
            instruction="Select a scope",
            context=None,
            selection_provider=selection_provider,
            initial_value="project",
        )

        # Act
        result = execute_selection_interaction(request=request)

        # Assert
        assert isinstance(result, Success)
        select.assert_called_once()
        kwargs = select.call_args.kwargs
        assert kwargs["message"] == "Select a scope"
        choices = kwargs["choices"]
        assert [choice.title for choice in choices] == ["Workspace", "Project"]
        assert [choice.value for choice in choices] == ["workspace", "project"]
        assert [choice.checked for choice in choices] == [False, True]
