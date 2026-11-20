from pathlib import Path
from unittest.mock import Mock

import gyomu_workflow.test.helpers.update as helpers_module
from gyomu_schema.protocols.interaction import InteractionExecutor
from gyomu_schema.schemas.config.test.model_defaults import (
    LiteralParameter,
    ParameterDefault,
)
from gyomu_schema.schemas.python.types import SymbolId
from gyomu_schema.schemas.testing.helper import HelperInventoryItem
from gyomu_test.helper.defaults.requirements import (
    ResolvedParameterDefault,
)
from gyomu_workflow.test.helpers.models import DefaultTypeParameterContext
from gyomu_workflow.test.helpers.update import (
    _create_helper_inventory,
    _define_helper_inventory_parameter,
)
from pytest import MonkeyPatch
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.python_analysis.test_support.helpers import (
    create_primitive_type,
    create_project_context,
    create_symbol_type,
    create_workspace_context,
    create_workspace_project,
)
from packages.schema.test_support.helpers import (
    create_gyomu_error,
    create_model_default,
)
from packages.schema.test_support.testing_helpers import (
    create_helper_inventory_item,
    create_helper_reconcile_result,
    create_parameter_info,
)
from packages.test.test_support.helpers import (
    create_configured_parameter_default,
    create_missing_parameter_default,
)


class TestDefineHelperInventoryParameter:
    def test_configured_parameter_default_is_returned_without_interaction(
        self,
        monkeypatch: MonkeyPatch,
    ) -> None:
        # Arrange
        parameter = create_parameter_info()
        configured = create_configured_parameter_default(parameter=parameter)

        inventory = Mock(spec=HelperInventoryItem)
        module_analysis = Mock()
        workspace_context = Mock()
        project_context = Mock()
        config_manager = Mock()
        interaction = Mock()

        resolve = Mock(return_value=Success(configured))
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.resolve_function_parameter_default",
            resolve,
        )

        # Act
        result = _define_helper_inventory_parameter(
            inventory=inventory,
            module_analysis=module_analysis,
            parameter_info=parameter,
            workspace_context=workspace_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )

        # Assert
        assert isinstance(result, Success)
        assert result.unwrap() == ParameterDefault(
            name=parameter.name,
            value=parameter.default,
        )

        resolve.assert_called_once_with(
            inventory=inventory,
            parameter_info=parameter,
            module_analysis=module_analysis,
            workspace_context=workspace_context,
            project_context=project_context,
            config_manager=config_manager,
        )
        interaction.execute.assert_not_called()

    def test_resolved_parameter_default_is_returned_without_interaction(
        self,
        monkeypatch: MonkeyPatch,
    ) -> None:
        # Arrange
        missing = create_missing_parameter_default(
            missing_types=(create_primitive_type(primitive_type="str"),)
        )
        parameter = missing.parameter
        resolved_default = LiteralParameter(value="resolved value")
        resolved = ResolvedParameterDefault(
            parameter=parameter,
            default=resolved_default,
        )

        inventory = Mock(spec=HelperInventoryItem)
        module_analysis = Mock()
        workspace_context = Mock()
        project_context = Mock()
        config_manager = Mock()
        interaction = Mock()

        resolve = Mock(return_value=Success(resolved))
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.resolve_function_parameter_default",
            resolve,
        )

        # Act
        result = _define_helper_inventory_parameter(
            inventory=inventory,
            module_analysis=module_analysis,
            parameter_info=parameter,
            workspace_context=workspace_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )

        # Assert
        assert isinstance(result, Success)
        assert result.unwrap() == ParameterDefault(
            name=parameter.name,
            value=resolved_default,
        )

        resolve.assert_called_once_with(
            inventory=inventory,
            parameter_info=parameter,
            module_analysis=module_analysis,
            workspace_context=workspace_context,
            project_context=project_context,
            config_manager=config_manager,
        )
        interaction.execute.assert_not_called()

    def test_missing_primitive_parameter_default_uses_direct_interaction(
        self,
        monkeypatch: MonkeyPatch,
    ) -> None:
        # Arrange
        missing = create_missing_parameter_default(
            missing_types=(create_primitive_type(primitive_type="str"),)
        )
        parameter = missing.parameter
        inventory = Mock(spec=HelperInventoryItem)
        inventory.target_identity = Mock()
        inventory.target_identity.symbol_id = SymbolId("project_a.module.Model")

        module_analysis = Mock()
        workspace_context = Mock()
        workspace_context.workspace_root.path = Path("/workspace")
        project_context = Mock()
        config_manager = Mock()
        interaction = Mock()

        resolved_default = LiteralParameter(value="new value")
        resolved = ResolvedParameterDefault(
            parameter=parameter,
            default=resolved_default,
        )

        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.resolve_function_parameter_default",
            Mock(return_value=Success(missing)),
        )
        root_workspace_context = Mock()
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.initialize_project_context",
            Mock(return_value=Success(root_workspace_context)),
        )
        direct = Mock(return_value=Success(resolved))
        document = Mock()
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.define_direct_parameter",
            direct,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.define_document_parameter",
            document,
        )

        # Act
        result = _define_helper_inventory_parameter(
            inventory=inventory,
            module_analysis=module_analysis,
            parameter_info=parameter,
            workspace_context=workspace_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )

        # Assert
        assert isinstance(result, Success)
        assert result.unwrap() == ParameterDefault(
            name=parameter.name,
            value=resolved_default,
        )
        direct.assert_called_once()
        direct.assert_called_once_with(
            parameter_context=DefaultTypeParameterContext(
                model_symbol_id=inventory.target_identity.symbol_id,
                parameter=missing,
                workspace_context=workspace_context,
                project_context=project_context,
                workspace_root_project_context=root_workspace_context,
            ),
            interaction=interaction,
        )
        document.assert_not_called()

    def test_missing_symbol_parameter_default_uses_document_interaction(
        self,
        monkeypatch: MonkeyPatch,
    ) -> None:
        # Arrange
        missing = create_missing_parameter_default(
            missing_types=(create_symbol_type(),)
        )
        parameter = missing.parameter
        inventory = Mock(spec=HelperInventoryItem)
        inventory.target_identity = Mock()
        inventory.target_identity.symbol_id = SymbolId("project_a.module.Model")

        module_analysis = Mock()
        workspace_context = Mock()
        workspace_context.workspace_root.path = Path("/workspace")
        project_context = Mock()
        config_manager = Mock()
        interaction = Mock()

        resolved_default = LiteralParameter(value="new value")
        resolved = ResolvedParameterDefault(
            parameter=parameter,
            default=resolved_default,
        )

        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.resolve_function_parameter_default",
            Mock(return_value=Success(missing)),
        )
        root_workspace_context = Mock()
        initialize = Mock(return_value=Success(root_workspace_context))
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.initialize_project_context",
            initialize,
        )
        direct = Mock(return_value=Success(resolved))
        document = Mock(return_value=Success(resolved))
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.define_direct_parameter",
            direct,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.define_document_parameter",
            document,
        )

        # Act
        result = _define_helper_inventory_parameter(
            inventory=inventory,
            module_analysis=module_analysis,
            parameter_info=parameter,
            workspace_context=workspace_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )

        # Assert
        assert isinstance(result, Success)
        assert result.unwrap() == ParameterDefault(
            name=parameter.name,
            value=resolved_default,
        )
        direct.assert_not_called()
        document.assert_called_once_with(
            parameter_context=DefaultTypeParameterContext(
                model_symbol_id=inventory.target_identity.symbol_id,
                parameter=missing,
                workspace_context=workspace_context,
                project_context=project_context,
                workspace_root_project_context=root_workspace_context,
            ),
            interaction=interaction,
        )

    def test_returns_failure_when_parameter_resolution_fails(
        self,
        monkeypatch: MonkeyPatch,
    ) -> None:
        # Arrange
        parameter = create_parameter_info()
        inventory = Mock(spec=HelperInventoryItem)
        module_analysis = Mock()
        workspace_context = Mock()
        project_context = Mock()
        config_manager = Mock()
        interaction = Mock()

        error = create_gyomu_error()
        resolve = Mock(return_value=Failure(error))

        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.resolve_function_parameter_default",
            resolve,
        )

        # Act
        result = _define_helper_inventory_parameter(
            inventory=inventory,
            module_analysis=module_analysis,
            parameter_info=parameter,
            workspace_context=workspace_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )

        # Assert
        assert isinstance(result, Failure)
        resolve.assert_called_once_with(
            inventory=inventory,
            parameter_info=parameter,
            module_analysis=module_analysis,
            workspace_context=workspace_context,
            project_context=project_context,
            config_manager=config_manager,
        )
        interaction.execute.assert_not_called()

    def test_returns_failure_when_workspace_root_project_context_initialization_fails(
        self,
        monkeypatch: MonkeyPatch,
    ) -> None:
        # Arrange
        missing = create_missing_parameter_default(
            missing_types=(create_primitive_type(primitive_type="str"),)
        )
        parameter = missing.parameter

        inventory = Mock(spec=HelperInventoryItem)
        inventory.target_identity = Mock()
        inventory.target_identity.symbol_id = "project_a.module.Model"

        module_analysis = Mock()
        workspace_context = Mock()
        workspace_context.workspace_root.path = Path("/workspace")
        project_context = Mock()
        config_manager = Mock()
        interaction = Mock()

        error = create_gyomu_error()

        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.resolve_function_parameter_default",
            Mock(return_value=Success(missing)),
        )
        initialize = Mock(return_value=Failure(error))
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.initialize_project_context",
            initialize,
        )

        direct = Mock()
        document = Mock()
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.define_direct_parameter",
            direct,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.define_document_parameter",
            document,
        )

        # Act
        result = _define_helper_inventory_parameter(
            inventory=inventory,
            module_analysis=module_analysis,
            parameter_info=parameter,
            workspace_context=workspace_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )

        # Assert
        assert isinstance(result, Failure)
        initialize.assert_called_once()
        direct.assert_not_called()
        document.assert_not_called()

    def test_returns_failure_when_direct_interaction_fails(
        self,
        monkeypatch: MonkeyPatch,
    ) -> None:
        # Arrange
        missing = create_missing_parameter_default(
            missing_types=(create_primitive_type(primitive_type="str"),)
        )
        parameter = missing.parameter

        inventory = Mock(spec=HelperInventoryItem)
        inventory.target_identity = Mock()
        inventory.target_identity.symbol_id = "project_a.module.Model"

        module_analysis = Mock()
        workspace_context = Mock()
        workspace_context.workspace_root.path = Path("/workspace")
        project_context = Mock()
        config_manager = Mock()
        interaction = Mock()

        error = create_gyomu_error()

        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.resolve_function_parameter_default",
            Mock(return_value=Success(missing)),
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.initialize_project_context",
            Mock(return_value=Success(Mock())),
        )

        direct = Mock(return_value=Failure(error))
        document = Mock()

        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.define_direct_parameter",
            direct,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.define_document_parameter",
            document,
        )

        # Act
        result = _define_helper_inventory_parameter(
            inventory=inventory,
            module_analysis=module_analysis,
            parameter_info=parameter,
            workspace_context=workspace_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )

        # Assert
        assert isinstance(result, Failure)
        direct.assert_called_once()
        document.assert_not_called()

    def test_returns_failure_when_document_interaction_fails(
        self,
        monkeypatch: MonkeyPatch,
    ) -> None:
        # Arrange
        missing = create_missing_parameter_default(
            missing_types=(create_symbol_type(),)
        )
        parameter = missing.parameter

        inventory = Mock(spec=HelperInventoryItem)
        inventory.target_identity = Mock()
        inventory.target_identity.symbol_id = "project_a.module.Model"

        module_analysis = Mock()
        workspace_context = Mock()
        workspace_context.workspace_root.path = Path("/workspace")
        project_context = Mock()
        config_manager = Mock()
        interaction = Mock()

        error = create_gyomu_error()

        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.resolve_function_parameter_default",
            Mock(return_value=Success(missing)),
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.initialize_project_context",
            Mock(return_value=Success(Mock())),
        )

        direct = Mock(return_value=Failure(error))
        document = Mock(return_value=Failure(error))

        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.define_direct_parameter",
            direct,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.define_document_parameter",
            document,
        )

        # Act
        result = _define_helper_inventory_parameter(
            inventory=inventory,
            module_analysis=module_analysis,
            parameter_info=parameter,
            workspace_context=workspace_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )

        # Assert
        assert isinstance(result, Failure)
        direct.assert_not_called()
        document.assert_called_once()


class TestCreateHelperInventory:
    def test_empty_create_returns_success(self) -> None:
        # Arrange
        workspace_context = Mock()
        project_context = Mock()
        config_manager = Mock()
        interaction = Mock()

        # Act
        result = _create_helper_inventory(
            create=(),
            workspace_context=workspace_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )

        # Assert
        assert isinstance(result, Success)

    def test_creates_model_default_and_updates_it(
        self,
        monkeypatch: MonkeyPatch,
    ) -> None:
        # Arrange
        target_identity = Mock()
        target_identity.get_symbol_name.return_value = "Model"

        parameter_info = create_parameter_info()
        inventory = create_helper_inventory_item(
            target_identity=target_identity,
            parameters=(parameter_info,),
        )

        module_analysis = Mock()
        file_analysis_context = (Mock(analysis=module_analysis), Mock())

        workspace_context = Mock()
        workspace_context.find_file_analysis_context.return_value = Success(
            file_analysis_context
        )
        project_context = Mock()
        config_manager = Mock()
        interaction = Mock()

        parameter_default = ParameterDefault(
            name=parameter_info.name,
            value=LiteralParameter(value="default value"),
        )

        define_parameter = Mock(return_value=Success(parameter_default))
        update_default = Mock(return_value=Success(None))

        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update._define_helper_inventory_parameter",
            define_parameter,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.update_model_default",
            update_default,
        )

        # Act
        result = _create_helper_inventory(
            create=(inventory,),
            workspace_context=workspace_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )

        # Assert
        assert isinstance(result, Success)

        workspace_context.find_file_analysis_context.assert_called_once_with(
            target_identity=target_identity,
        )
        define_parameter.assert_called_once_with(
            inventory=inventory,
            module_analysis=module_analysis,
            parameter_info=parameter_info,
            workspace_context=workspace_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )
        update_default.assert_called_once_with(
            project_context=project_context,
            target_identity=target_identity,
            model_default=create_model_default(
                class_name="Model",
                parameters=(parameter_default,),
            ),
        )

    def test_returns_failure_when_file_analysis_lookup_fails(
        self,
        monkeypatch: MonkeyPatch,
    ) -> None:
        # Arrange
        inventory = create_helper_inventory_item()
        workspace_context = Mock()
        error = create_gyomu_error()

        workspace_context.find_file_analysis_context.return_value = Failure(error)

        project_context = Mock()
        config_manager = Mock()
        interaction = Mock()

        define_parameter = Mock()
        update_default = Mock()

        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update._define_helper_inventory_parameter",
            define_parameter,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.update_model_default",
            update_default,
        )

        # Act
        result = _create_helper_inventory(
            create=(inventory,),
            workspace_context=workspace_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )

        # Assert
        assert isinstance(result, Failure)

        workspace_context.find_file_analysis_context.assert_called_once_with(
            target_identity=inventory.target_identity,
        )
        define_parameter.assert_not_called()
        update_default.assert_not_called()

    def test_returns_failure_when_file_analysis_context_is_none(
        self,
        monkeypatch: MonkeyPatch,
    ) -> None:
        # Arrange
        inventory = create_helper_inventory_item()
        workspace_context = Mock()
        workspace_context.find_file_analysis_context.return_value = Success(None)

        project_context = Mock()
        config_manager = Mock()
        interaction = Mock()

        define_parameter = Mock()
        update_default = Mock()

        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update._define_helper_inventory_parameter",
            define_parameter,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.update_model_default",
            update_default,
        )

        # Act
        result = _create_helper_inventory(
            create=(inventory,),
            workspace_context=workspace_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )

        # Assert
        assert isinstance(result, Failure)

        workspace_context.find_file_analysis_context.assert_called_once_with(
            target_identity=inventory.target_identity,
        )
        define_parameter.assert_not_called()
        update_default.assert_not_called()

    def test_returns_failure_when_parameter_definition_fails(
        self,
        monkeypatch: MonkeyPatch,
    ) -> None:
        # Arrange
        parameter_info = create_parameter_info()
        inventory = create_helper_inventory_item(
            parameters=(parameter_info,),
        )
        module_analysis = Mock()
        file_analysis_context = (Mock(analysis=module_analysis), Mock())

        workspace_context = Mock()
        workspace_context.find_file_analysis_context.return_value = Success(
            file_analysis_context
        )

        project_context = Mock()
        config_manager = Mock()
        interaction = Mock()

        error = create_gyomu_error()
        define_parameter = Mock(return_value=Failure(error))
        update_default = Mock()

        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update._define_helper_inventory_parameter",
            define_parameter,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.update_model_default",
            update_default,
        )

        # Act
        result = _create_helper_inventory(
            create=(inventory,),
            workspace_context=workspace_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )

        # Assert
        assert isinstance(result, Failure)

        workspace_context.find_file_analysis_context.assert_called_once_with(
            target_identity=inventory.target_identity,
        )
        define_parameter.assert_called_once_with(
            inventory=inventory,
            module_analysis=module_analysis,
            parameter_info=inventory.parameters[0],
            workspace_context=workspace_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )
        update_default.assert_not_called()

    def test_returns_failure_when_model_default_update_fails(
        self,
        monkeypatch: MonkeyPatch,
    ) -> None:
        # Arrange
        parameter_info = create_parameter_info()
        inventory = create_helper_inventory_item(
            parameters=(parameter_info,),
        )

        module_analysis = Mock()
        file_analysis_context = (Mock(analysis=module_analysis), Mock())

        workspace_context = Mock()
        workspace_context.find_file_analysis_context.return_value = Success(
            file_analysis_context
        )

        project_context = Mock()
        config_manager = Mock()
        interaction = Mock()

        parameter_default = ParameterDefault(
            name=parameter_info.name,
            value=LiteralParameter(value="default value"),
        )
        define_parameter = Mock(return_value=Success(parameter_default))
        update_default = Mock(return_value=Failure(create_gyomu_error()))

        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update._define_helper_inventory_parameter",
            define_parameter,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.update_model_default",
            update_default,
        )

        # Act
        result = _create_helper_inventory(
            create=(inventory,),
            workspace_context=workspace_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )

        # Assert
        assert isinstance(result, Failure)

        define_parameter.assert_called_once()
        update_default.assert_called_once_with(
            project_context=project_context,
            target_identity=inventory.target_identity,
            model_default=create_model_default(
                class_name=inventory.target_identity.get_symbol_name(),
                parameters=(parameter_default,),
            ),
        )

    def test_creates_model_defaults_for_multiple_inventory_items(
        self,
        monkeypatch: MonkeyPatch,
    ) -> None:
        # Arrange
        parameter_info_1 = create_parameter_info()
        inventory_1 = create_helper_inventory_item(
            parameters=(parameter_info_1,),
        )
        parameter_info_2 = create_parameter_info()
        inventory_2 = create_helper_inventory_item(
            parameters=(parameter_info_2,),
        )

        module_analysis_1 = Mock()
        module_analysis_2 = Mock()
        workspace_context = Mock()
        workspace_context.find_file_analysis_context.side_effect = [
            Success((Mock(analysis=module_analysis_1), Mock())),
            Success((Mock(analysis=module_analysis_2), Mock())),
        ]

        project_context = Mock()
        config_manager = Mock()
        interaction = Mock()

        parameter_default_1 = ParameterDefault(
            name=parameter_info_1.name,
            value=LiteralParameter(value="default 1"),
        )
        parameter_default_2 = ParameterDefault(
            name=parameter_info_2.name,
            value=LiteralParameter(value="default 2"),
        )
        define_parameter = Mock(
            side_effect=[
                Success(parameter_default_1),
                Success(parameter_default_2),
            ]
        )
        update_default = Mock(return_value=Success(None))

        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update._define_helper_inventory_parameter",
            define_parameter,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.update_model_default",
            update_default,
        )

        # Act
        result = _create_helper_inventory(
            create=(inventory_1, inventory_2),
            workspace_context=workspace_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )

        # Assert
        assert isinstance(result, Success)

        assert workspace_context.find_file_analysis_context.call_count == 2
        assert define_parameter.call_count == 2
        assert update_default.call_count == 2

        update_default.assert_any_call(
            project_context=project_context,
            target_identity=inventory_1.target_identity,
            model_default=create_model_default(
                class_name=inventory_1.target_identity.get_symbol_name(),
                parameters=(parameter_default_1,),
            ),
        )
        update_default.assert_any_call(
            project_context=project_context,
            target_identity=inventory_2.target_identity,
            model_default=create_model_default(
                class_name=inventory_2.target_identity.get_symbol_name(),
                parameters=(parameter_default_2,),
            ),
        )


class TestUpdateHelperInventories:
    def test_create_is_empty(
        self,
        mocker: MockerFixture,
    ) -> None:
        workspace_context = create_workspace_context()
        workspace_project_context = create_workspace_project()
        project_context = create_project_context()
        reconcile_result = create_helper_reconcile_result()

        mocker.patch(
            "gyomu_workflow.test.helpers.update.reconcile_package",
            return_value=Success((reconcile_result, project_context)),
        )
        create_mock = mocker.patch.object(
            helpers_module,
            "_create_helper_inventory",
        )
        config_manager_mock = mocker.patch.object(
            helpers_module,
            "ConfigManager",
        )

        interaction = Mock(spec=InteractionExecutor)

        result = helpers_module.update_helper_inventories(
            workspace_context=workspace_context,
            workspace_project_context=workspace_project_context,
            interaction=interaction,
        )

        assert result == Success(None)
        create_mock.assert_not_called()
        config_manager_mock.assert_called_once_with()

    def test_create_success(
        self,
        mocker: MockerFixture,
    ) -> None:
        workspace_context = create_workspace_context()
        workspace_project_context = create_workspace_project()
        project_context = create_project_context()
        reconcile_result = create_helper_reconcile_result(
            create=(create_helper_inventory_item(),),
        )
        mocker.patch(
            "gyomu_workflow.test.helpers.update.reconcile_package",
            return_value=Success((reconcile_result, project_context)),
        )

        config_manager_mock = mocker.patch.object(
            helpers_module,
            "ConfigManager",
        )
        create_mock = mocker.patch.object(
            helpers_module,
            "_create_helper_inventory",
            return_value=Success(None),
        )

        interaction = Mock(spec=InteractionExecutor)

        result = helpers_module.update_helper_inventories(
            workspace_context=workspace_context,
            workspace_project_context=workspace_project_context,
            interaction=interaction,
        )

        assert result == Success(None)

        config_manager = config_manager_mock.return_value
        create_mock.assert_called_once_with(
            create=reconcile_result.create,
            workspace_context=workspace_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )

    def test_create_failure(
        self,
        mocker: MockerFixture,
    ) -> None:
        workspace_context = create_workspace_context()
        workspace_project_context = create_workspace_project()
        project_context = create_project_context()
        reconcile_result = create_helper_reconcile_result(
            create=(create_helper_inventory_item(),),
        )
        mocker.patch(
            "gyomu_workflow.test.helpers.update.reconcile_package",
            return_value=Success((reconcile_result, project_context)),
        )

        mocker.patch.object(
            helpers_module,
            "ConfigManager",
        )

        error = create_gyomu_error("create failed")
        failure = Failure(error)
        create_mock = mocker.patch.object(
            helpers_module,
            "_create_helper_inventory",
            return_value=failure,
        )

        interaction = Mock(spec=InteractionExecutor)

        result = helpers_module.update_helper_inventories(
            workspace_context=workspace_context,
            workspace_project_context=workspace_project_context,
            interaction=interaction,
        )

        assert result is failure
        create_mock.assert_called_once()

    def test_reconcile_failure(
        self,
        mocker: MockerFixture,
    ) -> None:
        workspace_context = create_workspace_context()
        workspace_project_context = create_workspace_project()

        error = create_gyomu_error("reconcile failed")
        failure = Failure(error)

        reconcile_mock = mocker.patch(
            "gyomu_workflow.test.helpers.update.reconcile_package",
            return_value=failure,
        )
        create_mock = mocker.patch.object(
            helpers_module,
            "_create_helper_inventory",
        )
        config_manager_mock = mocker.patch.object(
            helpers_module,
            "ConfigManager",
        )

        interaction = Mock(spec=InteractionExecutor)

        result = helpers_module.update_helper_inventories(
            workspace_context=workspace_context,
            workspace_project_context=workspace_project_context,
            interaction=interaction,
        )

        assert result is failure

        reconcile_mock.assert_called_once_with(
            workspace_context=workspace_context,
            workspace_project_context=workspace_project_context,
        )
        create_mock.assert_not_called()
        config_manager_mock.assert_not_called()
