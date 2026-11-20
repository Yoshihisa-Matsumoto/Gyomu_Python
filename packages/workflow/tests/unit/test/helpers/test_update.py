from unittest.mock import Mock

import gyomu_workflow.test.helpers.update as helpers_module
from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.protocols.interaction import InteractionExecutor
from gyomu_schema.schemas.config.test.model_defaults import (
    LiteralParameter,
    ModelDefault,
)
from gyomu_schema.schemas.testing.helper import HelperInventoryItem
from gyomu_test.helper.defaults.requirements import (
    ResolvedParameterDefault,
)
from gyomu_workflow.test.helpers.update import (
    _create_helper_inventory,
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


class TestCreateHelperInventory:
    def test_resolved_parameters_are_saved_as_model_default(
        self,
        monkeypatch,
    ) -> None:
        # Arrange
        missing = create_missing_parameter_default(
            missing_types=(create_primitive_type(),)
        )
        parameter = missing.parameter
        resolved_default = LiteralParameter(value="hello")
        resolved = ResolvedParameterDefault(
            parameter=parameter,
            default=resolved_default,
        )

        target_identity = Mock()
        target_identity.get_symbol_name.return_value = "ExampleModel"

        create_item = Mock(spec=HelperInventoryItem)
        create_item.target_identity = target_identity

        workspace_context = Mock()
        project_context = Mock()
        config_manager = Mock()
        interaction = Mock()

        resolve = Mock(return_value=Success((resolved,)))
        update = Mock(return_value=Success(None))

        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.resolve_function_parameter_defaults",
            resolve,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.update_model_default",
            update,
        )

        # Act
        result = _create_helper_inventory(
            create=(create_item,),
            workspace_context=workspace_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )

        # Assert
        assert isinstance(result, Success)
        assert result.unwrap() is None

        resolve.assert_called_once_with(
            inventory=create_item,
            workspace_context=workspace_context,
            project_context=project_context,
            config_manager=config_manager,
        )

        update.assert_called_once()
        kwargs = update.call_args.kwargs
        assert kwargs["project_context"] is project_context
        assert kwargs["target_identity"] is target_identity

        model_default = kwargs["model_default"]
        assert isinstance(model_default, ModelDefault)
        assert model_default.symbol_name == "ExampleModel"
        assert model_default.parameters == (
            # ParameterDefault の構築結果を確認
            model_default.parameters[0],
        )
        assert model_default.parameters[0].name == parameter.name
        assert model_default.parameters[0].value == resolved_default

    def test_resolve_parameter_failure_does_not_update_model_default(
        self,
        monkeypatch,
    ) -> None:
        create_item = Mock(spec=HelperInventoryItem)
        workspace_context = Mock()
        project_context = Mock()
        config_manager = Mock()
        interaction = Mock()

        error = GyomuError(
            "resolve failed",
            operation="test",
            domain="test",
            reason="external_failure",
        )
        resolve = Mock(return_value=Failure(error))
        update = Mock(return_value=Success(None))

        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.resolve_function_parameter_defaults",
            resolve,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.update_model_default",
            update,
        )

        result = _create_helper_inventory(
            create=(create_item,),
            workspace_context=workspace_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )

        assert isinstance(result, Failure)
        assert result.failure().message == "fail to resolve function parameters"
        update.assert_not_called()
        interaction.execute.assert_not_called()

    def test_update_model_default_failure_is_wrapped(
        self,
        monkeypatch,
    ) -> None:
        create_item = Mock(spec=HelperInventoryItem)
        target_identity = Mock()
        target_identity.get_symbol_name.return_value = "ExampleModel"
        create_item.target_identity = target_identity

        workspace_context = Mock()
        project_context = Mock()
        config_manager = Mock()
        interaction = Mock()

        resolve = Mock(return_value=Success(()))
        error = GyomuError(
            "update failed",
            operation="test",
            domain="test",
            reason="external_failure",
        )
        update = Mock(return_value=Failure(error))

        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.resolve_function_parameter_defaults",
            resolve,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.update_model_default",
            update,
        )

        result = _create_helper_inventory(
            create=(create_item,),
            workspace_context=workspace_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )

        assert isinstance(result, Failure)
        assert result.failure().message == "fail to update function parameter"
        update.assert_called_once()
        interaction.execute.assert_not_called()

    def test_missing_parameter_default_is_defined_and_saved(
        self,
        monkeypatch,
    ) -> None:
        missing = create_missing_parameter_default(
            missing_types=(create_primitive_type(primitive_type="str"),)
        )
        resolved_value = LiteralParameter(value="provided by user")
        resolved = ResolvedParameterDefault(
            parameter=missing.parameter,
            default=resolved_value,
        )

        target_identity = Mock()
        target_identity.get_symbol_name.return_value = "ExampleModel"

        create_item = Mock(spec=HelperInventoryItem)
        create_item.target_identity = target_identity

        workspace_context = Mock()
        project_context = Mock()
        config_manager = Mock()
        interaction = Mock()

        resolve = Mock(return_value=Success((missing,)))
        define = Mock(return_value=Success(resolved))
        update = Mock(return_value=Success(None))

        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.resolve_function_parameter_defaults",
            resolve,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.define_direct_parameter",
            define,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.update_model_default",
            update,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.initialize_project_context",
            Mock(return_value=Success(Mock())),
        )

        result = _create_helper_inventory(
            create=(create_item,),
            workspace_context=workspace_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )

        assert isinstance(result, Success)
        assert result.unwrap() is None

        define.assert_called_once()
        parameter_context = define.call_args.kwargs["parameter_context"]
        assert parameter_context.parameter is missing
        assert parameter_context.workspace_context is workspace_context
        assert parameter_context.project_context is project_context
        assert define.call_args.kwargs["interaction"] is interaction

        update.assert_called_once()
        model_default = update.call_args.kwargs["model_default"]
        assert isinstance(model_default, ModelDefault)
        assert model_default.symbol_name == "ExampleModel"
        assert len(model_default.parameters) == 1
        assert model_default.parameters[0].name == missing.parameter.name
        assert model_default.parameters[0].value == resolved_value

    def test_configured_parameter_default_is_saved_without_interaction(
        self,
        monkeypatch,
    ) -> None:
        configured_parameter = create_parameter_info()
        configured_default = create_configured_parameter_default(
            parameter=configured_parameter
        )

        target_identity = Mock()
        target_identity.get_symbol_name.return_value = "ExampleModel"

        create_item = Mock(spec=HelperInventoryItem)
        create_item.target_identity = target_identity

        workspace_context = Mock()
        project_context = Mock()
        config_manager = Mock()
        interaction = Mock()

        resolve = Mock(return_value=Success((configured_default,)))
        define = Mock()
        update = Mock(return_value=Success(None))

        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.resolve_function_parameter_defaults",
            resolve,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.define_direct_parameter",
            define,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.update_model_default",
            update,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.initialize_project_context",
            Mock(return_value=Success(Mock())),
        )
        result = _create_helper_inventory(
            create=(create_item,),
            workspace_context=workspace_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )

        assert isinstance(result, Success)
        assert result.unwrap() is None

        define.assert_not_called()
        update.assert_called_once()

        model_default = update.call_args.kwargs["model_default"]
        assert isinstance(model_default, ModelDefault)
        assert model_default.symbol_name == "ExampleModel"
        assert len(model_default.parameters) == 1
        assert model_default.parameters[0].name == configured_parameter.name
        assert model_default.parameters[0].value == configured_parameter.default

    def test_empty_create_returns_success_without_dependencies(self) -> None:
        result = _create_helper_inventory(
            create=(),
            workspace_context=Mock(),
            project_context=Mock(),
            config_manager=Mock(),
            interaction=Mock(),
        )

        assert isinstance(result, Success)
        assert result.unwrap() is None

    def test_missing_complex_parameter_default_uses_document_interaction(
        self,
        monkeypatch: MonkeyPatch,
    ) -> None:
        missing = create_missing_parameter_default(
            missing_types=(create_symbol_type(),)
        )
        resolved_value = LiteralParameter(value="provided by document")
        resolved = ResolvedParameterDefault(
            parameter=missing.parameter,
            default=resolved_value,
        )

        target_identity = Mock()
        target_identity.get_symbol_name.return_value = "ExampleModel"

        create_item = Mock(spec=HelperInventoryItem)
        create_item.target_identity = target_identity

        workspace_context = Mock()
        project_context = Mock()
        config_manager = Mock()
        interaction = Mock()

        resolve = Mock(return_value=Success((missing,)))
        define_direct = Mock()
        define_document = Mock(return_value=Success(resolved))
        update = Mock(return_value=Success(None))

        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.resolve_function_parameter_defaults",
            resolve,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.define_direct_parameter",
            define_direct,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.define_document_parameter",
            define_document,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.update_model_default",
            update,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.initialize_project_context",
            Mock(return_value=Success(Mock())),
        )

        result = _create_helper_inventory(
            create=(create_item,),
            workspace_context=workspace_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )

        assert isinstance(result, Success)
        assert result.unwrap() is None

        define_direct.assert_not_called()
        define_document.assert_called_once()

        parameter_context = define_document.call_args.kwargs["parameter_context"]
        assert parameter_context.parameter is missing
        assert parameter_context.workspace_context is workspace_context
        assert parameter_context.project_context is project_context
        assert define_document.call_args.kwargs["interaction"] is interaction

        update.assert_called_once()
        model_default = update.call_args.kwargs["model_default"]
        assert isinstance(model_default, ModelDefault)
        assert model_default.symbol_name == "ExampleModel"
        assert len(model_default.parameters) == 1
        assert model_default.parameters[0].name == missing.parameter.name
        assert model_default.parameters[0].value == resolved_value

    def test_initialize_workspace_root_project_context_failure(
        self,
        monkeypatch,
    ) -> None:
        missing = create_missing_parameter_default(
            missing_types=(create_primitive_type(primitive_type="str"),)
        )
        create_item = Mock(spec=HelperInventoryItem)
        create_item.target_identity = Mock()

        workspace_context = Mock()
        project_context = Mock()
        config_manager = Mock()
        interaction = Mock()

        resolve = Mock(return_value=Success((missing,)))
        error = create_gyomu_error()
        initialize = Mock(return_value=Failure(error))
        define = Mock()
        update = Mock()

        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.resolve_function_parameter_defaults",
            resolve,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.initialize_project_context",
            initialize,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.define_direct_parameter",
            define,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.update_model_default",
            update,
        )

        result = _create_helper_inventory(
            create=(create_item,),
            workspace_context=workspace_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )

        assert isinstance(result, Failure)
        assert result.failure().message == (
            "fail to initialize workspace root project context"
        )
        initialize.assert_called_once()
        define.assert_not_called()
        update.assert_not_called()
        interaction.execute.assert_not_called()

    def test_document_interaction_failure_does_not_update_model_default(
        self,
        monkeypatch,
    ) -> None:
        missing = create_missing_parameter_default(
            missing_types=(create_symbol_type(),)
        )
        create_item = Mock(spec=HelperInventoryItem)
        create_item.target_identity = Mock()

        workspace_context = Mock()
        project_context = Mock()
        config_manager = Mock()
        interaction = Mock()

        resolve = Mock(return_value=Success((missing,)))
        initialize = Mock(return_value=Success(Mock()))
        error = create_gyomu_error()
        define_document = Mock(return_value=Failure(error))
        update = Mock()

        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.resolve_function_parameter_defaults",
            resolve,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.initialize_project_context",
            initialize,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.define_document_parameter",
            define_document,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.update_model_default",
            update,
        )

        result = _create_helper_inventory(
            create=(create_item,),
            workspace_context=workspace_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )

        assert isinstance(result, Failure)
        assert result.failure() is error
        define_document.assert_called_once()
        update.assert_not_called()

    def test_direct_interaction_failure_does_not_update_model_default(
        self,
        monkeypatch,
    ) -> None:
        missing = create_missing_parameter_default(
            missing_types=(create_primitive_type(primitive_type="str"),)
        )
        create_item = Mock(spec=HelperInventoryItem)
        create_item.target_identity = Mock()

        workspace_context = Mock()
        project_context = Mock()
        config_manager = Mock()
        interaction = Mock()

        resolve = Mock(return_value=Success((missing,)))
        initialize = Mock(return_value=Success(Mock()))
        error = create_gyomu_error()
        define_direct = Mock(return_value=Failure(error))
        update = Mock()

        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.resolve_function_parameter_defaults",
            resolve,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.initialize_project_context",
            initialize,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.define_direct_parameter",
            define_direct,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.update_model_default",
            update,
        )

        result = _create_helper_inventory(
            create=(create_item,),
            workspace_context=workspace_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )

        assert isinstance(result, Failure)
        assert result.failure() is error
        define_direct.assert_called_once()
        update.assert_not_called()


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
