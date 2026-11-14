from pathlib import Path
from types import SimpleNamespace
from typing import cast
from unittest.mock import Mock, call

import gyomu_workflow.test.helpers as helpers_module
import pytest
from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.error.validation import ValidationError
from gyomu_schema.protocols.interaction import InteractionExecutor
from gyomu_schema.schemas.config.test.model_defaults import (
    LiteralParameter,
    ModelDefault,
)
from gyomu_schema.schemas.interaction.request import (
    InputMode,
    InteractionDirectRequest,
)
from gyomu_schema.schemas.interaction.result import (
    InteractionAccepted,
    InteractionCancelled,
    InteractionRejected,
)
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.schemas.testing.helper import HelperInventoryItem
from gyomu_test.helper.defaults.requirements import (
    MissingParameterDefault,
    ResolvedParameterDefault,
)
from gyomu_workflow.test.helpers import (
    DefaultTypeParameterContext,
    PrimitiveValueCodec,
    _build_interaction_request,
    _create_helper_inventory,
    _define_parameter,
)
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.python_analysis.test_support.helpers import (
    create_analysis_error,
    create_primitive_type,
    create_project_context,
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


class TestPrimitiveValueCodec:
    @pytest.mark.parametrize(
        ("primitive_type", "raw_input", "expected"),
        [
            ("str", "hello", "hello"),
            ("int", "42", 42),
            ("bool", "true", True),
            ("bool", "false", False),
            ("float", "3.14", 3.14),
        ],
    )
    def test_parse_supported_primitive_value(
        self,
        primitive_type: str,
        raw_input: str,
        expected: str | int | bool | float,
    ) -> None:
        parameter: MissingParameterDefault = create_missing_parameter_default(
            missing_types=(create_primitive_type(primitive_type=primitive_type),)
        )
        context = cast(
            DefaultTypeParameterContext,
            SimpleNamespace(parameter=parameter),
        )

        result = PrimitiveValueCodec().parse(raw_input=raw_input, context=context)

        assert isinstance(result, Success)
        assert result.unwrap() == LiteralParameter(value=expected)

    @pytest.mark.parametrize(
        ("raw_input", "expected"),
        [
            (" TRUE ", True),
            ("False", False),
        ],
    )
    def test_parse_bool_ignores_case_and_surrounding_whitespace(
        self,
        raw_input: str,
        expected: bool,
    ) -> None:
        parameter = create_missing_parameter_default(
            missing_types=(create_primitive_type(primitive_type="bool"),)
        )
        context = cast(
            DefaultTypeParameterContext,
            SimpleNamespace(parameter=parameter),
        )

        result = PrimitiveValueCodec().parse(raw_input=raw_input, context=context)

        assert isinstance(result, Success)
        assert result.unwrap() == LiteralParameter(value=expected)

    @pytest.mark.parametrize(
        ("primitive_type", "raw_input"),
        [
            ("int", "not-an-int"),
            ("float", "not-a-float"),
            ("bool", "yes"),
        ],
    )
    def test_parse_invalid_input_returns_failure(
        self,
        primitive_type: str,
        raw_input: str,
    ) -> None:
        parameter = create_missing_parameter_default(
            missing_types=(create_primitive_type(primitive_type=primitive_type),)
        )
        context = cast(
            DefaultTypeParameterContext,
            SimpleNamespace(parameter=parameter),
        )

        result = PrimitiveValueCodec().parse(raw_input=raw_input, context=context)

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), ValidationError)

    def test_parse_unsupported_type_returns_failure(self) -> None:
        parameter = create_missing_parameter_default(
            missing_types=(create_primitive_type(primitive_type="complex"),)
        )
        context = cast(
            DefaultTypeParameterContext,
            SimpleNamespace(parameter=parameter),
        )

        result = PrimitiveValueCodec().parse(raw_input="1+2j", context=context)

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), ValidationError)
        assert "Unsupported Type" in result.failure().message


class TestBuildInteractionRequest:
    def test_supported_primitive_type_returns_interaction_request(self) -> None:
        parameter = create_missing_parameter_default(
            missing_types=(create_primitive_type(primitive_type="str"),)
        )
        context = cast(
            DefaultTypeParameterContext,
            SimpleNamespace(parameter=parameter),
        )

        result = _build_interaction_request(parameter_context=context)

        assert isinstance(result, Success)
        request = result.unwrap()

        assert isinstance(request, InteractionDirectRequest)
        assert request.instruction == "Please define your type parameter for "
        assert request.input_mode == InputMode.DIRECT
        assert request.context is context
        assert isinstance(request.codec, PrimitiveValueCodec)
        assert request.initial_value is None

    def test_unsupported_type_returns_failure(self) -> None:
        parameter = create_missing_parameter_default(
            missing_types=(create_primitive_type(primitive_type="complex"),)
        )
        context = cast(
            DefaultTypeParameterContext,
            SimpleNamespace(parameter=parameter),
        )

        result = _build_interaction_request(parameter_context=context)

        assert isinstance(result, Failure)
        error = result.failure()

        assert isinstance(error, GyomuError)
        assert error.reason == "out_of_bounds"


class TestDefineParameter:
    def _create_context(
        self, primitive_type: str = "str"
    ) -> DefaultTypeParameterContext:
        parameter = create_missing_parameter_default(
            missing_types=(create_primitive_type(primitive_type=primitive_type),)
        )
        return cast(
            DefaultTypeParameterContext,
            SimpleNamespace(parameter=parameter),
        )

    def test_accepted_returns_resolved_parameter_default(self) -> None:
        context = self._create_context()
        executor = Mock(spec=InteractionExecutor)
        value = LiteralParameter(value="hello")
        executor.execute.return_value = Success(InteractionAccepted(value=value))

        result = _define_parameter(
            parameter_context=context,
            interaction=executor,
        )

        assert isinstance(result, Success)
        resolved = result.unwrap()
        assert isinstance(resolved, ResolvedParameterDefault)
        assert resolved.parameter is context.parameter.parameter
        assert resolved.default == value

        executor.execute.assert_called_once()
        request = executor.execute.call_args.kwargs["request"]
        assert isinstance(request, InteractionDirectRequest)
        assert request.context is context
        assert isinstance(request.codec, PrimitiveValueCodec)

    def test_rejected_returns_failure(self) -> None:
        context = self._create_context()
        executor = Mock(spec=InteractionExecutor)
        executor.execute.return_value = Success(InteractionRejected())

        result = _define_parameter(
            parameter_context=context,
            interaction=executor,
        )

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), GyomuError)
        assert result.failure().reason == "external_failure"
        executor.execute.assert_called_once()

    def test_cancelled_returns_failure(self) -> None:
        context = self._create_context()
        executor = Mock(spec=InteractionExecutor)
        executor.execute.return_value = Success(InteractionCancelled())

        result = _define_parameter(
            parameter_context=context,
            interaction=executor,
        )

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), GyomuError)
        assert result.failure().reason == "external_failure"
        executor.execute.assert_called_once()

    def test_executor_failure_is_propagated(self) -> None:
        context = self._create_context()
        executor = Mock(spec=InteractionExecutor)
        error = GyomuError(
            "interaction failed",
            operation="test",
            domain="test",
            reason="external_failure",
        )
        executor.execute.return_value = Failure(error)

        result = _define_parameter(
            parameter_context=context,
            interaction=executor,
        )

        assert isinstance(result, Failure)
        assert result.failure() is error
        executor.execute.assert_called_once()

    def test_unsupported_type_does_not_call_executor(self) -> None:
        context = self._create_context(primitive_type="complex")
        executor = Mock(spec=InteractionExecutor)

        result = _define_parameter(
            parameter_context=context,
            interaction=executor,
        )

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), GyomuError)
        assert result.failure().reason == "out_of_bounds"
        executor.execute.assert_not_called()


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
            "gyomu_workflow.test.helpers.resolve_function_parameter_defaults",
            resolve,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update_model_default",
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
            "gyomu_workflow.test.helpers.resolve_function_parameter_defaults",
            resolve,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update_model_default",
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
            "gyomu_workflow.test.helpers.resolve_function_parameter_defaults",
            resolve,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update_model_default",
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
            "gyomu_workflow.test.helpers.resolve_function_parameter_defaults",
            resolve,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers._define_parameter",
            define,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update_model_default",
            update,
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
            "gyomu_workflow.test.helpers.resolve_function_parameter_defaults",
            resolve,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers._define_parameter",
            define,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update_model_default",
            update,
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


class TestReconcile:
    def test_success(self, mocker: MockerFixture) -> None:
        # Arrange
        workspace_context = create_workspace_context()
        workspace_project = create_workspace_project()
        project_context = create_project_context()

        expected = (create_helper_inventory_item(),)
        existing = ()
        reconcile_result = create_helper_reconcile_result()

        initialize_project = mocker.patch.object(
            helpers_module,
            "initialize_project_from_workspace",
            return_value=project_context,
        )
        collect_expected = mocker.patch.object(
            helpers_module,
            "collect_model_helper_inventory",
            return_value=Success(expected),
        )
        initialize_root = mocker.patch.object(
            helpers_module,
            "initialize_project_context",
            return_value=Success(project_context),
        )
        collect_existing = mocker.patch.object(
            helpers_module,
            "collect_existing_helper_inventory",
            return_value=Success(existing),
        )
        reconcile = mocker.patch.object(
            helpers_module,
            "reconcile",
            return_value=reconcile_result,
        )

        # Act
        result = helpers_module._reconcile(
            workspace_context=workspace_context,
            workspace_project_context=workspace_project,
        )

        # Assert
        assert result == Success((reconcile_result, project_context))

        initialize_project.assert_called_once_with(
            workspace_path=workspace_context.workspace_root.path,
            project=workspace_project,
        )
        collect_expected.assert_called_once_with(
            project_context,
            workspace_context,
        )
        initialize_root.assert_called_once_with(
            project_root=workspace_context.workspace_root.path,
            source_root=ProjectRelativePath(Path(".")),
        )
        collect_existing.assert_called_once_with(
            root=project_context,
            target_project=project_context,
        )
        reconcile.assert_called_once_with(
            existing=existing,
            expected=expected,
        )

        # 呼び出し順序も確認する
        assert [
            initialize_project.call_args,
            collect_expected.call_args,
            initialize_root.call_args,
            collect_existing.call_args,
            reconcile.call_args,
        ] == [
            call(
                workspace_path=workspace_context.workspace_root.path,
                project=workspace_project,
            ),
            call(project_context, workspace_context),
            call(
                project_root=workspace_context.workspace_root.path,
                source_root=ProjectRelativePath(Path(".")),
            ),
            call(root=project_context, target_project=project_context),
            call(existing=existing, expected=expected),
        ]

    def test_collect_model_helper_inventory_failure(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        workspace_context = create_workspace_context()
        workspace_project = create_workspace_project()
        project_context = create_project_context()
        error = create_gyomu_error(message="test error")

        mocker.patch.object(
            helpers_module,
            "initialize_project_from_workspace",
            return_value=project_context,
        )
        mocker.patch.object(
            helpers_module,
            "collect_model_helper_inventory",
            return_value=Failure(error),
        )
        initialize_root = mocker.patch.object(
            helpers_module,
            "initialize_project_context",
        )
        collect_existing = mocker.patch.object(
            helpers_module,
            "collect_existing_helper_inventory",
        )
        reconcile = mocker.patch.object(
            helpers_module,
            "reconcile",
        )

        # Act
        result = helpers_module._reconcile(
            workspace_context=workspace_context,
            workspace_project_context=workspace_project,
        )

        # Assert
        assert isinstance(result, Failure)
        assert result.failure().message == "fail to collect inventories from models"
        initialize_root.assert_not_called()
        collect_existing.assert_not_called()
        reconcile.assert_not_called()

    def test_initialize_project_context_failure(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        workspace_context = create_workspace_context()
        workspace_project = create_workspace_project()
        project_context = create_project_context()
        error = create_analysis_error(message="test error")

        mocker.patch.object(
            helpers_module,
            "initialize_project_from_workspace",
            return_value=project_context,
        )
        mocker.patch.object(
            helpers_module,
            "collect_model_helper_inventory",
            return_value=Success(()),
        )
        mocker.patch.object(
            helpers_module,
            "initialize_project_context",
            return_value=Failure(error),
        )
        collect_existing = mocker.patch.object(
            helpers_module,
            "collect_existing_helper_inventory",
        )
        reconcile = mocker.patch.object(
            helpers_module,
            "reconcile",
        )

        # Act
        result = helpers_module._reconcile(
            workspace_context=workspace_context,
            workspace_project_context=workspace_project,
        )

        # Assert
        assert isinstance(result, Failure)
        assert result.failure().message == "fail to initialize project"
        collect_existing.assert_not_called()
        reconcile.assert_not_called()

    def test_collect_existing_helper_inventory_failure(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        workspace_context = create_workspace_context()
        workspace_project = create_workspace_project()
        project_context = create_project_context()
        root_context = create_project_context(
            project_root=workspace_context.workspace_root.path,
            source_root=ProjectRelativePath(Path(".")),
        )
        error = create_gyomu_error(message="test error")

        mocker.patch.object(
            helpers_module,
            "initialize_project_from_workspace",
            return_value=project_context,
        )
        mocker.patch.object(
            helpers_module,
            "collect_model_helper_inventory",
            return_value=Success(()),
        )
        initialize_root = mocker.patch.object(
            helpers_module,
            "initialize_project_context",
            return_value=Success(root_context),
        )
        collect_existing = mocker.patch.object(
            helpers_module,
            "collect_existing_helper_inventory",
            return_value=Failure(error),
        )
        reconcile = mocker.patch.object(
            helpers_module,
            "reconcile",
        )

        # Act
        result = helpers_module._reconcile(
            workspace_context=workspace_context,
            workspace_project_context=workspace_project,
        )

        # Assert
        assert isinstance(result, Failure)
        assert result.failure().message == "fail to gather existing inventories"

        initialize_root.assert_called_once_with(
            project_root=workspace_context.workspace_root.path,
            source_root=ProjectRelativePath(Path(".")),
        )
        collect_existing.assert_called_once_with(
            root=root_context,
            target_project=project_context,
        )
        reconcile.assert_not_called()


class TestUpdateHelperInventories:
    def test_create_is_empty(
        self,
        mocker: MockerFixture,
    ) -> None:
        workspace_context = create_workspace_context()
        workspace_project_context = create_workspace_project()
        project_context = create_project_context()
        reconcile_result = create_helper_reconcile_result()

        mocker.patch.object(
            helpers_module,
            "_reconcile",
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

        mocker.patch.object(
            helpers_module,
            "_reconcile",
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

        mocker.patch.object(
            helpers_module,
            "_reconcile",
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

        reconcile_mock = mocker.patch.object(
            helpers_module,
            "_reconcile",
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
