from unittest.mock import Mock

from gyomu_schema.schemas.config.test.model_defaults import (
    PrimitiveDefault,
    SymbolDefault,
)
from gyomu_test.helper.defaults.requirements import MissingParameterDefault
from gyomu_workflow.test.helpers._internal.type_parameter_config import (
    configure_primitive_literal_type_parameter_default,
    configure_type_parameter_default,
    save_primitive_literal_type_parameter_default_in_workspace,
    save_symbol_type_parameter_default_in_workspace,
)
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.python_analysis.test_support.helpers import create_symbol_type
from packages.schema.test_support.helpers import (
    create_gyomu_error,
    create_primitive_default,
    create_symbol_default,
)
from packages.workflow.test_support.helpers import (
    create_default_primitive_literal_type_parameter_context,
    create_default_type_parameter_context,
)


class TestSavePrimitiveLiteralTypeParameterDefaultInWorkspace:
    def test_returns_failure_when_config_existence_check_fails(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        parameter_context = create_default_primitive_literal_type_parameter_context()
        parameter = create_primitive_default().parameter
        error = create_gyomu_error()
        mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "has_workspace_primitive_type_parameter_default_config",
            return_value=Failure(error),
        )
        save_mock = mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "save_primitive_parameter_default_config"
        )

        # Act
        result = save_primitive_literal_type_parameter_default_in_workspace(
            parameter_context=parameter_context,
            parameter=parameter,
        )

        # Assert
        assert isinstance(result, Failure)
        assert result.failure() == error
        save_mock.assert_not_called()

    def test_saves_config_when_config_does_not_exist(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        parameter_context = create_default_primitive_literal_type_parameter_context()
        parameter = create_primitive_default().parameter
        mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "has_workspace_primitive_type_parameter_default_config",
            return_value=Success(False),
        )
        save_mock = mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "save_primitive_parameter_default_config",
            return_value=Success(None),
        )

        # Act
        result = save_primitive_literal_type_parameter_default_in_workspace(
            parameter_context=parameter_context,
            parameter=parameter,
        )

        # Assert
        assert result == Success(None)
        save_mock.assert_called_once_with(
            workspace_context=parameter_context.workspace_context,
            project_context=None,
            primitive_default=PrimitiveDefault(
                type_name=parameter_context.parameter_type_name(),
                parameter=parameter,
            ),
        )

    def test_does_not_save_config_when_config_already_exists(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        parameter_context = create_default_primitive_literal_type_parameter_context()
        parameter = create_primitive_default().parameter
        mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "has_workspace_primitive_type_parameter_default_config",
            return_value=Success(True),
        )
        save_mock = mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "save_primitive_parameter_default_config"
        )

        # Act
        result = save_primitive_literal_type_parameter_default_in_workspace(
            parameter_context=parameter_context,
            parameter=parameter,
        )

        # Assert
        assert result == Success(None)
        save_mock.assert_not_called()


class TestConfigurePrimitiveLiteralTypeParameterDefault:
    def test_returns_failure_when_config_existence_check_fails(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        parameter_context = create_default_primitive_literal_type_parameter_context()
        parameter = create_primitive_default().parameter
        error = create_gyomu_error()
        mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "has_workspace_primitive_type_parameter_default_config",
            return_value=Failure(error),
        )
        select_mock = mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "select_config_place_to_save"
        )
        save_mock = mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "save_primitive_parameter_default_config"
        )

        # Act
        result = configure_primitive_literal_type_parameter_default(
            parameter_context=parameter_context,
            interaction=Mock(),
            parameter=parameter,
        )

        # Assert
        assert isinstance(result, Failure)
        assert result.failure() == error
        select_mock.assert_not_called()
        save_mock.assert_not_called()

    def test_does_not_select_place_or_save_when_config_already_exists(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        parameter_context = create_default_primitive_literal_type_parameter_context()
        parameter = create_primitive_default().parameter
        mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "has_workspace_primitive_type_parameter_default_config",
            return_value=Success(True),
        )
        select_mock = mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "select_config_place_to_save"
        )
        save_mock = mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "save_primitive_parameter_default_config"
        )

        # Act
        result = configure_primitive_literal_type_parameter_default(
            parameter_context=parameter_context,
            interaction=Mock(),
            parameter=parameter,
        )

        # Assert
        assert result == Success(None)
        select_mock.assert_not_called()
        save_mock.assert_not_called()

    def test_does_not_save_when_config_place_selection_is_cancelled(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        parameter_context = create_default_primitive_literal_type_parameter_context()
        parameter = create_primitive_default().parameter
        mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "has_workspace_primitive_type_parameter_default_config",
            return_value=Success(False),
        )
        select_mock = mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "select_config_place_to_save",
            return_value=Success(None),
        )
        save_mock = mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "save_primitive_parameter_default_config"
        )

        # Act
        result = configure_primitive_literal_type_parameter_default(
            parameter_context=parameter_context,
            interaction=Mock(),
            parameter=parameter,
        )

        # Assert
        assert result == Success(None)
        select_mock.assert_called_once()
        save_mock.assert_not_called()

    def test_returns_failure_when_config_place_selection_fails(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        parameter_context = create_default_primitive_literal_type_parameter_context()
        parameter = create_primitive_default().parameter
        error = create_gyomu_error()
        mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "has_workspace_primitive_type_parameter_default_config",
            return_value=Success(False),
        )
        mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "select_config_place_to_save",
            return_value=Failure(error),
        )
        save_mock = mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "save_primitive_parameter_default_config"
        )

        # Act
        result = configure_primitive_literal_type_parameter_default(
            parameter_context=parameter_context,
            interaction=Mock(),
            parameter=parameter,
        )

        # Assert
        assert isinstance(result, Failure)
        assert result.failure() == error
        save_mock.assert_not_called()

    def test_saves_config_when_config_place_is_selected(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        parameter_context = create_default_primitive_literal_type_parameter_context()
        parameter = create_primitive_default().parameter
        save_workspace = parameter_context.workspace_context
        save_project = parameter_context.project_context
        mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "has_workspace_primitive_type_parameter_default_config",
            return_value=Success(False),
        )
        mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "select_config_place_to_save",
            return_value=Success((save_workspace, save_project)),
        )
        save_mock = mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "save_primitive_parameter_default_config",
            return_value=Success(None),
        )

        # Act
        result = configure_primitive_literal_type_parameter_default(
            parameter_context=parameter_context,
            interaction=Mock(),
            parameter=parameter,
        )

        # Assert
        assert result == Success(None)
        save_mock.assert_called_once_with(
            workspace_context=save_workspace,
            project_context=save_project,
            primitive_default=PrimitiveDefault(
                type_name=parameter_context.parameter_type_name(),
                parameter=parameter,
            ),
        )

    def test_wraps_error_when_saving_config_fails(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        parameter_context = create_default_primitive_literal_type_parameter_context()
        parameter = create_primitive_default().parameter
        error = create_gyomu_error()
        mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "has_workspace_primitive_type_parameter_default_config",
            return_value=Success(False),
        )
        mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "select_config_place_to_save",
            return_value=Success(
                (
                    parameter_context.workspace_context,
                    parameter_context.project_context,
                )
            ),
        )
        save_mock = mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "save_primitive_parameter_default_config",
            return_value=Failure(error),
        )
        wrap_mock = mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "wrap_gyomu_error",
            return_value=error,
        )

        # Act
        result = configure_primitive_literal_type_parameter_default(
            parameter_context=parameter_context,
            interaction=Mock(),
            parameter=parameter,
        )

        # Assert
        assert isinstance(result, Failure)
        assert result.failure() == error
        save_mock.assert_called_once()
        wrap_mock.assert_called_once_with(
            error=error,
            message="fail to save type parameter",
        )


class TestSaveSymbolTypeParameterDefaultInWorkspace:
    def test_returns_failure_when_config_existence_check_fails(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        parameter_context = create_default_type_parameter_context()
        parameter = create_symbol_default().parameter
        resolved_type = create_symbol_type()
        error = create_gyomu_error()
        mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "has_workspace_symbol_type_parameter_default_config",
            return_value=Failure(error),
        )
        save_mock = mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "save_symbol_parameter_default_config"
        )

        # Act
        result = save_symbol_type_parameter_default_in_workspace(
            parameter_context=parameter_context,
            parameter=parameter,
            resolved_type=resolved_type,
        )

        # Assert
        assert isinstance(result, Failure)
        assert result.failure() == error
        save_mock.assert_not_called()

    def test_saves_config_when_config_does_not_exist(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        parameter_context = create_default_type_parameter_context()
        parameter = create_symbol_default().parameter
        resolved_type = create_symbol_type()
        mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "has_workspace_symbol_type_parameter_default_config",
            return_value=Success(False),
        )
        save_mock = mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "save_symbol_parameter_default_config",
            return_value=Success(None),
        )

        # Act
        result = save_symbol_type_parameter_default_in_workspace(
            parameter_context=parameter_context,
            parameter=parameter,
            resolved_type=resolved_type,
        )

        # Assert
        assert result == Success(None)
        save_mock.assert_called_once_with(
            workspace_context=parameter_context.workspace_context,
            project_context=None,
            module_path=parameter_context.model_identity.get_module_name(),
            symbol_default=SymbolDefault(
                symbol_name=parameter_context.model_identity.get_symbol_name(),
                parameter=parameter,
            ),
        )

    def test_does_not_save_config_when_config_already_exists(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        parameter_context = create_default_type_parameter_context()
        parameter = create_symbol_default().parameter
        resolved_type = create_symbol_type()
        mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "has_workspace_symbol_type_parameter_default_config",
            return_value=Success(True),
        )
        save_mock = mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "save_symbol_parameter_default_config"
        )

        # Act
        result = save_symbol_type_parameter_default_in_workspace(
            parameter_context=parameter_context,
            parameter=parameter,
            resolved_type=resolved_type,
        )

        # Assert
        assert result == Success(None)
        save_mock.assert_not_called()


class TestConfigureTypeParameterDefault:
    def test_returns_failure_when_confirmation_fails(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        existing_parameter_default = create_primitive_default().parameter
        resolved_types = (create_symbol_type(),)
        expected_parameter_info = (
            create_default_type_parameter_context().parameter.parameter
        )
        workspace_context = create_default_type_parameter_context().workspace_context
        project_context = create_default_type_parameter_context().project_context
        error = create_gyomu_error()
        mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "simple_confirm",
            return_value=Failure(error),
        )
        resolve_mock = mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "resolve_primitive_parameter_type"
        )
        primitive_save_mock = mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "save_primitive_parameter_default_config"
        )
        symbol_save_mock = mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "save_symbol_parameter_default_config"
        )

        # Act
        result = configure_type_parameter_default(
            existing_parameter_default=existing_parameter_default,
            resolved_types=resolved_types,
            expected_parameter_info=expected_parameter_info,
            workspace_context=workspace_context,
            project_context=project_context,
            interaction=Mock(),
        )

        # Assert
        assert isinstance(result, Failure)
        assert result.failure() == error
        resolve_mock.assert_not_called()
        primitive_save_mock.assert_not_called()
        symbol_save_mock.assert_not_called()

    def test_returns_failure_when_confirmation_is_cancelled(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        parameter_context = create_default_type_parameter_context()
        existing_parameter_default = create_primitive_default().parameter
        resolved_types = (create_symbol_type(),)
        expected_parameter_info = parameter_context.parameter.parameter

        mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "simple_confirm",
            return_value=Success(None),
        )
        resolve_mock = mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "resolve_primitive_parameter_type"
        )
        primitive_save_mock = mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "save_primitive_parameter_default_config"
        )
        symbol_save_mock = mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "save_symbol_parameter_default_config"
        )

        # Act
        result = configure_type_parameter_default(
            existing_parameter_default=existing_parameter_default,
            resolved_types=resolved_types,
            expected_parameter_info=expected_parameter_info,
            workspace_context=parameter_context.workspace_context,
            project_context=parameter_context.project_context,
            interaction=Mock(),
        )

        # Assert
        assert isinstance(result, Failure)
        assert result.failure().message == "canceled the process"
        assert result.failure().operation == "helper"
        assert result.failure().domain == "test"
        assert result.failure().reason == "out_of_bounds"
        resolve_mock.assert_not_called()
        primitive_save_mock.assert_not_called()
        symbol_save_mock.assert_not_called()

    def test_saves_primitive_type_parameter_default_when_confirmed(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        parameter_context = create_default_type_parameter_context()
        existing_parameter_default = create_primitive_default().parameter
        resolved_types = (create_symbol_type(),)
        expected_parameter_info = parameter_context.parameter.parameter
        parameter_type_name = "str"

        mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "simple_confirm",
            return_value=Success(True),
        )
        mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "resolve_primitive_parameter_type",
            return_value=(parameter_type_name, resolved_types),
        )
        save_mock = mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "save_primitive_parameter_default_config",
            return_value=Success(None),
        )
        symbol_save_mock = mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "save_symbol_parameter_default_config"
        )

        # Act
        result = configure_type_parameter_default(
            existing_parameter_default=existing_parameter_default,
            resolved_types=resolved_types,
            expected_parameter_info=expected_parameter_info,
            workspace_context=parameter_context.workspace_context,
            project_context=parameter_context.project_context,
            interaction=Mock(),
        )

        # Assert
        assert result == Success(None)
        save_mock.assert_called_once_with(
            workspace_context=parameter_context.workspace_context,
            project_context=parameter_context.project_context,
            primitive_default=PrimitiveDefault(
                type_name=parameter_type_name,
                parameter=existing_parameter_default,
            ),
        )
        symbol_save_mock.assert_not_called()

    def test_saves_symbol_type_parameter_default_when_confirmed(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        parameter_context = create_default_type_parameter_context()
        existing_parameter_default = create_symbol_default().parameter
        resolved_type = create_symbol_type()
        resolved_types = (resolved_type,)
        expected_parameter_info = parameter_context.parameter.parameter
        identity = resolved_type.symbol.identity

        mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "simple_confirm",
            return_value=Success(True),
        )
        resolve_mock = mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "resolve_primitive_parameter_type",
            return_value=None,
        )
        primitive_save_mock = mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "save_primitive_parameter_default_config"
        )
        symbol_save_mock = mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "save_symbol_parameter_default_config",
            return_value=Success(None),
        )

        # Act
        result = configure_type_parameter_default(
            existing_parameter_default=existing_parameter_default,
            resolved_types=resolved_types,
            expected_parameter_info=expected_parameter_info,
            workspace_context=parameter_context.workspace_context,
            project_context=parameter_context.project_context,
            interaction=Mock(),
        )

        # Assert
        assert result == Success(None)
        resolve_mock.assert_called_once_with(
            parameter=MissingParameterDefault(
                parameter=expected_parameter_info,
                missing_types=resolved_types,
            )
        )
        symbol_save_mock.assert_called_once_with(
            workspace_context=parameter_context.workspace_context,
            project_context=parameter_context.project_context,
            module_path=identity.get_module_name(),
            symbol_default=SymbolDefault(
                symbol_name=identity.get_symbol_name(),
                parameter=existing_parameter_default,
            ),
        )
        primitive_save_mock.assert_not_called()

    def test_wraps_error_when_saving_primitive_type_parameter_default_fails(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        parameter_context = create_default_type_parameter_context()
        existing_parameter_default = create_primitive_default().parameter
        resolved_types = (create_symbol_type(),)
        expected_parameter_info = parameter_context.parameter.parameter
        error = create_gyomu_error()

        mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "simple_confirm",
            return_value=Success(True),
        )
        mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "resolve_primitive_parameter_type",
            return_value=("str", resolved_types),
        )
        mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "save_primitive_parameter_default_config",
            return_value=Failure(error),
        )
        wrap_mock = mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "wrap_gyomu_error",
            return_value=error,
        )

        # Act
        result = configure_type_parameter_default(
            existing_parameter_default=existing_parameter_default,
            resolved_types=resolved_types,
            expected_parameter_info=expected_parameter_info,
            workspace_context=parameter_context.workspace_context,
            project_context=parameter_context.project_context,
            interaction=Mock(),
        )

        # Assert
        assert isinstance(result, Failure)
        wrap_mock.assert_called_once_with(
            error=error,
            message="fail to save primitive type parameter",
        )

    def test_wraps_error_when_saving_symbol_type_parameter_default_fails(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        parameter_context = create_default_type_parameter_context()
        existing_parameter_default = create_symbol_default().parameter
        resolved_type = create_symbol_type()
        resolved_types = (resolved_type,)
        expected_parameter_info = parameter_context.parameter.parameter
        error = create_gyomu_error()

        mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "simple_confirm",
            return_value=Success(True),
        )
        mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "resolve_primitive_parameter_type",
            return_value=None,
        )
        mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "save_symbol_parameter_default_config",
            return_value=Failure(error),
        )
        wrap_mock = mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "wrap_gyomu_error",
            return_value=error,
        )

        # Act
        result = configure_type_parameter_default(
            existing_parameter_default=existing_parameter_default,
            resolved_types=resolved_types,
            expected_parameter_info=expected_parameter_info,
            workspace_context=parameter_context.workspace_context,
            project_context=parameter_context.project_context,
            interaction=Mock(),
        )

        # Assert
        assert isinstance(result, Failure)
        wrap_mock.assert_called_once_with(
            error=error,
            message="fail to save symbol type parameter",
        )

    def test_does_not_save_when_confirmation_is_rejected(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        parameter_context = create_default_type_parameter_context()
        existing_parameter_default = create_primitive_default().parameter
        resolved_types = (create_symbol_type(),)
        expected_parameter_info = parameter_context.parameter.parameter

        mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "simple_confirm",
            return_value=Success(False),
        )
        resolve_mock = mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "resolve_primitive_parameter_type"
        )
        primitive_save_mock = mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "save_primitive_parameter_default_config"
        )
        symbol_save_mock = mocker.patch(
            "gyomu_workflow.test.helpers._internal.type_parameter_config."
            "save_symbol_parameter_default_config"
        )

        # Act
        result = configure_type_parameter_default(
            existing_parameter_default=existing_parameter_default,
            resolved_types=resolved_types,
            expected_parameter_info=expected_parameter_info,
            workspace_context=parameter_context.workspace_context,
            project_context=parameter_context.project_context,
            interaction=Mock(),
        )

        # Assert
        assert result == Success(None)
        resolve_mock.assert_not_called()
        primitive_save_mock.assert_not_called()
        symbol_save_mock.assert_not_called()
