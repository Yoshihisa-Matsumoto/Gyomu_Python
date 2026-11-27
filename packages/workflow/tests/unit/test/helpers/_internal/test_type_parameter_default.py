from unittest.mock import Mock

from gyomu_schema.schemas.interaction.request import InteractionSelectRequest
from gyomu_schema.schemas.interaction.result import (
    InteractionAccepted,
    InteractionCancelled,
)
from gyomu_workflow.test.helpers._internal.type_parameter_default import (
    ConfigPlaceSelectionProvider,
    _build_config_place_selection_request,
    has_workspace_primitive_type_parameter_default_config,
    has_workspace_symbol_type_parameter_default_config,
    select_config_place_to_save,
)
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.python_analysis.test_support.helpers import (
    create_project_context,
    create_symbol_type,
)
from packages.schema.test_support.helpers import (
    create_gyomu_error,
    create_primitive_default,
    create_symbol_default,
)
from packages.workflow.test_support.helpers import (
    create_default_package_type_config_place_context,
    create_default_primitive_literal_type_config_place_context,
    create_default_primitive_literal_type_parameter_context,
    create_default_symbol_type_config_place_context,
    create_default_type_parameter_context,
)


class TestSelectConfigPlaceToSave:
    def test_returns_failure_when_interaction_fails(self) -> None:
        # Arrange
        context = create_default_primitive_literal_type_config_place_context()
        error = create_gyomu_error()
        interaction = Mock()
        interaction.execute.return_value = Failure(error)

        # Act
        result = select_config_place_to_save(
            context=context,
            interaction=interaction,
        )

        # Assert
        assert isinstance(result, Failure)
        assert result.failure() == error
        interaction.execute.assert_called_once()

    def test_returns_success_none_when_interaction_is_cancelled(self) -> None:
        # Arrange
        context = create_default_primitive_literal_type_config_place_context()
        interaction = Mock()
        interaction.execute.return_value = Success(InteractionCancelled())

        # Act
        result = select_config_place_to_save(
            context=context,
            interaction=interaction,
        )

        # Assert
        assert isinstance(result, Success)
        assert result.unwrap() is None
        interaction.execute.assert_called_once()

    def test_returns_workspace_context_when_workspace_root_is_selected(
        self,
    ) -> None:
        # Arrange
        context = create_default_primitive_literal_type_config_place_context()
        interaction = Mock()
        interaction.execute.return_value = Success(
            InteractionAccepted(value=context.workspace_context)
        )

        # Act
        result = select_config_place_to_save(
            context=context,
            interaction=interaction,
        )

        # Assert
        assert isinstance(result, Success)
        assert result.unwrap() == (context.workspace_context, None)
        interaction.execute.assert_called_once()

    def test_returns_test_project_context_when_test_project_is_selected(
        self,
    ) -> None:
        # Arrange
        context = create_default_primitive_literal_type_config_place_context()
        interaction = Mock()
        interaction.execute.return_value = Success(
            InteractionAccepted(value=context.test_project_context)
        )

        # Act
        result = select_config_place_to_save(
            context=context,
            interaction=interaction,
        )

        # Assert
        assert isinstance(result, Success)
        assert result.unwrap() == (
            context.workspace_context,
            context.test_project_context,
        )
        interaction.execute.assert_called_once()

    def test_returns_model_project_context_when_model_project_is_selected(
        self,
    ) -> None:
        # Arrange
        context = create_default_symbol_type_config_place_context(
            model_project_context=create_project_context()
        )
        assert context.model_project_context is not None

        interaction = Mock()
        interaction.execute.return_value = Success(
            InteractionAccepted(value=context.model_project_context)
        )

        # Act
        result = select_config_place_to_save(
            context=context,
            interaction=interaction,
        )

        # Assert
        assert isinstance(result, Success)
        assert result.unwrap() == (
            context.workspace_context,
            context.model_project_context,
        )
        interaction.execute.assert_called_once()


class TestHasWorkspacePrimitiveTypeParameterDefaultConfig:
    def test_returns_true_when_config_exists(self, mocker: MockerFixture) -> None:
        # Arrange
        parameter_context = create_default_primitive_literal_type_parameter_context()
        mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_default."
            "load_workspace_primitive_parameter_default_config",
            return_value=Success(create_primitive_default()),
        )

        # Act
        result = has_workspace_primitive_type_parameter_default_config(
            parameter_context=parameter_context,
        )

        # Assert
        assert result == Success(True)

    def test_returns_false_when_config_does_not_exist(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        parameter_context = create_default_primitive_literal_type_parameter_context()
        mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_default."
            "load_workspace_primitive_parameter_default_config",
            return_value=Success(None),
        )

        # Act
        result = has_workspace_primitive_type_parameter_default_config(
            parameter_context=parameter_context,
        )

        # Assert
        assert result == Success(False)

    def test_returns_wrapped_failure_when_loading_config_fails(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        parameter_context = create_default_primitive_literal_type_parameter_context()
        error = create_gyomu_error()
        mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_default."
            "load_workspace_primitive_parameter_default_config",
            return_value=Failure(error),
        )

        # Act
        result = has_workspace_primitive_type_parameter_default_config(
            parameter_context=parameter_context,
        )

        # Assert
        assert isinstance(result, Failure)
        assert result.failure().message == "fail to load type parameter"


class TestHasWorkspaceSymbolTypeParameterDefaultConfig:
    def test_returns_true_when_config_exists(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        parameter_context = create_default_type_parameter_context()
        resolved_type = create_symbol_type()
        mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_default."
            "load_workspace_symbol_parameter_default_config",
            return_value=Success(create_symbol_default()),
        )

        # Act
        result = has_workspace_symbol_type_parameter_default_config(
            parameter_context=parameter_context,
            resolved_type=resolved_type,
        )

        # Assert
        assert result == Success(True)

    def test_returns_false_when_config_does_not_exist(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        parameter_context = create_default_type_parameter_context()
        resolved_type = create_symbol_type()
        mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_default."
            "load_workspace_symbol_parameter_default_config",
            return_value=Success(None),
        )

        # Act
        result = has_workspace_symbol_type_parameter_default_config(
            parameter_context=parameter_context,
            resolved_type=resolved_type,
        )

        # Assert
        assert result == Success(False)

    def test_returns_wrapped_failure_when_loading_config_fails(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        parameter_context = create_default_type_parameter_context()
        resolved_type = create_symbol_type()
        error = create_gyomu_error()
        mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_default."
            "load_workspace_symbol_parameter_default_config",
            return_value=Failure(error),
        )

        # Act
        result = has_workspace_symbol_type_parameter_default_config(
            parameter_context=parameter_context,
            resolved_type=resolved_type,
        )

        # Assert
        assert isinstance(result, Failure)
        assert result.failure().message == "fail to load type parameter"


class TestConfigPlaceSelectionProvider:
    def test_returns_workspace_and_test_project_selections_for_primitive_type(
        self,
    ) -> None:
        # Arrange
        context = create_default_primitive_literal_type_config_place_context()
        provider = ConfigPlaceSelectionProvider()

        # Act
        result = provider.create_selections(context)

        # Assert
        assert isinstance(result, Success)
        selections = result.unwrap()
        assert len(selections) == 2
        assert selections[0].label == "Workspace Root"
        assert selections[0].value is context.workspace_context
        assert selections[1].label == (
            f"Test Project: {context.test_project_context.config.name}"
        )
        assert selections[1].value is context.test_project_context

    def test_includes_model_project_selection_for_symbol_type(
        self,
    ) -> None:
        # Arrange
        context = create_default_symbol_type_config_place_context(
            model_project_context=create_project_context()
        )
        provider = ConfigPlaceSelectionProvider()

        # Act
        result = provider.create_selections(context)

        # Assert
        assert isinstance(result, Success)
        selections = result.unwrap()
        assert len(selections) == 3
        assert selections[0].label == "Workspace Root"
        assert selections[1].label == (
            f"Test Project: {context.test_project_context.config.name}"
        )
        assert context.model_project_context
        assert selections[2].label == (
            f"Model Project: {context.model_project_context.config.name}"
        )
        assert selections[2].value is context.model_project_context

    def test_excludes_model_project_selection_when_model_project_context_is_none(
        self,
    ) -> None:
        # Arrange
        context = create_default_symbol_type_config_place_context(
            model_project_context=None
        )
        provider = ConfigPlaceSelectionProvider()

        # Act
        result = provider.create_selections(context)

        # Assert
        assert isinstance(result, Success)
        selections = result.unwrap()
        assert len(selections) == 2
        assert all(
            not selection.label.startswith("Model Project: ")
            for selection in selections
        )

    def test_includes_model_project_selection_for_package_type(
        self,
    ) -> None:
        # Arrange
        context = create_default_package_type_config_place_context(
            model_project_context=create_project_context()
        )
        provider = ConfigPlaceSelectionProvider()

        # Act
        result = provider.create_selections(context)

        # Assert
        assert isinstance(result, Success)
        selections = result.unwrap()
        assert len(selections) == 3
        assert context.model_project_context is not None
        assert selections[2].label == (
            f"Model Project: {context.model_project_context.config.name}"
        )
        assert selections[2].value is context.model_project_context


class TestBuildConfigPlaceSelectionRequest:
    def test_builds_selection_request_with_parameter_information(
        self,
    ) -> None:
        # Arrange
        context = create_default_primitive_literal_type_config_place_context()

        # Act
        request = _build_config_place_selection_request(context)

        # Assert
        assert isinstance(request, InteractionSelectRequest)
        assert request.instruction == (
            "Please choose where to save for "
            f"{context.parameter.name}:"
            f"{context.parameter.parameter_type.text}"
        )
        assert request.context is context
        assert isinstance(request.selection_provider, ConfigPlaceSelectionProvider)
