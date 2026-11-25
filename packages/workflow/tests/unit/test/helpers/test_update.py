from pathlib import Path
from unittest.mock import Mock

import gyomu_workflow.test.helpers.update as helpers_module
from gyomu_schema.protocols.interaction import InteractionExecutor
from gyomu_schema.schemas.config.test.model_defaults import (
    LiteralParameter,
    ParameterDefault,
)
from gyomu_schema.schemas.python.types import ProjectRelativePath, SymbolId
from gyomu_schema.schemas.testing.helper import HelperInventoryItem
from gyomu_schema.schemas.types import FullPath
from gyomu_test.helper.defaults.requirements import (
    ResolvedParameterDefault,
)
from gyomu_workflow.test.helpers._internal.models import (
    DefaultPrimitiveLiteralTypeParameterContext,
    DefaultTypeParameterContext,
)
from gyomu_workflow.test.helpers.update import (
    _create_helper_inventory,
    _create_helper_inventory_item,
    _define_helper_inventory_parameter,
    _resolve_helper_inventory_item,
    _validate_helper_file,
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
    create_module_analysis,
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
from packages.test.tests.unit.helper.helpers import create_gyomu_test_error


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
        workspace_root_project_context = Mock()
        project_context = Mock()
        config_manager = Mock()
        interaction = Mock()

        resolve = Mock(return_value=Success((configured, ())))
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
            workspace_root_project_context=workspace_root_project_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )

        # Assert
        assert isinstance(result, Success)
        assert result.unwrap() == (
            ParameterDefault(
                name=parameter.name,
                value=parameter.default,
            ),
            (),
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
            parameter=parameter, default=resolved_default, referenced_types=()
        )

        inventory = Mock(spec=HelperInventoryItem)
        module_analysis = Mock()
        workspace_context = Mock()
        workspace_root_project_context = Mock()
        project_context = Mock()
        config_manager = Mock()
        interaction = Mock()

        resolve = Mock(return_value=Success((resolved, ())))
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
            workspace_root_project_context=workspace_root_project_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )

        # Assert
        assert isinstance(result, Success)
        assert result.unwrap() == (
            ParameterDefault(
                name=parameter.name,
                value=resolved_default,
            ),
            (),
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
        missing_type = create_primitive_type(primitive_type="str")
        missing = create_missing_parameter_default(missing_types=(missing_type,))
        parameter = missing.parameter
        inventory = Mock(spec=HelperInventoryItem)
        inventory.target_identity = Mock()
        inventory.target_identity.symbol_id = SymbolId("project_a.module.Model")

        module_analysis = Mock()
        workspace_context = Mock()
        workspace_context.workspace_root.path = Path("/workspace")
        workspace_root_project_context = Mock()
        project_context = Mock()
        config_manager = Mock()
        interaction = Mock()

        resolved_default = LiteralParameter(value="new value")
        resolved = ResolvedParameterDefault(
            parameter=parameter, default=resolved_default, referenced_types=()
        )

        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.resolve_function_parameter_default",
            Mock(return_value=Success((missing, ()))),
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.initialize_project_context",
            Mock(return_value=Success(workspace_root_project_context)),
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
            workspace_root_project_context=workspace_root_project_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )

        # Assert
        assert isinstance(result, Success)
        assert result.unwrap() == (
            ParameterDefault(
                name=parameter.name,
                value=resolved_default,
            ),
            (),
        )
        direct.assert_called_once()
        direct.assert_called_once_with(
            parameter_context=DefaultPrimitiveLiteralTypeParameterContext(
                model_identity=inventory.target_identity,
                parameter=missing,
                workspace_context=workspace_context,
                project_context=project_context,
                workspace_root_project_context=workspace_root_project_context,
                config_manager=config_manager,
                resolved_type=missing_type,
            ),
            interaction=interaction,
        )
        document.assert_not_called()

    def test_missing_symbol_parameter_default_uses_document_interaction(
        self,
        monkeypatch: MonkeyPatch,
    ) -> None:
        # Arrange
        missing_type = create_symbol_type()
        missing = create_missing_parameter_default(missing_types=(missing_type,))
        parameter = missing.parameter
        inventory = Mock(spec=HelperInventoryItem)
        inventory.target_identity = Mock()
        inventory.target_identity.symbol_id = SymbolId("project_a.module.Model")

        module_analysis = Mock()
        workspace_context = Mock()
        workspace_context.workspace_root.path = Path("/workspace")
        workspace_root_project_context = Mock()
        project_context = Mock()
        config_manager = Mock()
        interaction = Mock()

        resolved_default = LiteralParameter(value="new value")
        resolved = ResolvedParameterDefault(
            parameter=parameter, default=resolved_default, referenced_types=()
        )

        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.resolve_function_parameter_default",
            Mock(return_value=Success((missing, ()))),
        )
        initialize = Mock(return_value=Success(workspace_root_project_context))
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
            workspace_root_project_context=workspace_root_project_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )

        # Assert
        assert isinstance(result, Success)
        assert result.unwrap() == (
            ParameterDefault(
                name=parameter.name,
                value=resolved_default,
            ),
            (),
        )
        direct.assert_not_called()
        document.assert_called_once_with(
            parameter_context=DefaultTypeParameterContext(
                model_identity=inventory.target_identity,
                parameter=missing,
                workspace_context=workspace_context,
                project_context=project_context,
                workspace_root_project_context=workspace_root_project_context,
                config_manager=config_manager,
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
        workspace_root_project_context = Mock()
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
            workspace_root_project_context=workspace_root_project_context,
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
        workspace_root_project_context = Mock()
        project_context = Mock()
        config_manager = Mock()
        interaction = Mock()

        error = create_gyomu_error()

        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.resolve_function_parameter_default",
            Mock(return_value=Success((missing, ()))),
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
            workspace_root_project_context=workspace_root_project_context,
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
        workspace_root_project_context = Mock()
        project_context = Mock()
        config_manager = Mock()
        interaction = Mock()

        error = create_gyomu_error()

        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.resolve_function_parameter_default",
            Mock(return_value=Success((missing, ()))),
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
            workspace_root_project_context=workspace_root_project_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )

        # Assert
        assert isinstance(result, Failure)
        direct.assert_not_called()
        document.assert_called_once()


class TestResolveHelperInventoryItem:
    def test_creates_model_default_and_updates_it(
        self, monkeypatch: MonkeyPatch, tmp_path
    ) -> None:
        # Arrange
        target_identity = Mock()
        target_identity.get_symbol_name.return_value = "Model"

        parameter_info = create_parameter_info()
        inventory = create_helper_inventory_item(
            target_identity=target_identity,
            parameters=(parameter_info,),
        )

        module_analysis = create_module_analysis()
        file_analysis_context = (Mock(analysis=module_analysis), Mock())

        workspace_context = Mock()
        workspace_context.find_file_analysis_context.return_value = Success(
            file_analysis_context
        )
        workspace_root_project_context = create_project_context(
            project_root=FullPath(tmp_path), source_root=ProjectRelativePath(Path(""))
        )
        project_context = Mock()
        project_context.project_root = FullPath(tmp_path)
        config_manager = Mock()
        interaction = Mock()

        parameter_default = ParameterDefault(
            name=parameter_info.name,
            value=LiteralParameter(value="default value"),
        )

        define_parameter = Mock(return_value=Success((parameter_default, ())))
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
        result = _resolve_helper_inventory_item(
            item=inventory,
            workspace_context=workspace_context,
            workspace_root_project_context=workspace_root_project_context,
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
            workspace_root_project_context=workspace_root_project_context,
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
        workspace_root_project_context = Mock()
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
        result = _resolve_helper_inventory_item(
            item=inventory,
            workspace_context=workspace_context,
            workspace_root_project_context=workspace_root_project_context,
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
        workspace_root_project_context = Mock()

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
        result = _resolve_helper_inventory_item(
            item=inventory,
            workspace_context=workspace_context,
            workspace_root_project_context=workspace_root_project_context,
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
        workspace_root_project_context = Mock()

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
        result = _resolve_helper_inventory_item(
            item=inventory,
            workspace_context=workspace_context,
            workspace_root_project_context=workspace_root_project_context,
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
            workspace_root_project_context=workspace_root_project_context,
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
        workspace_root_project_context = Mock()

        project_context = Mock()
        config_manager = Mock()
        interaction = Mock()

        parameter_default = ParameterDefault(
            name=parameter_info.name,
            value=LiteralParameter(value="default value"),
        )
        define_parameter = Mock(return_value=Success((parameter_default, ())))
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
        result = _resolve_helper_inventory_item(
            item=inventory,
            workspace_context=workspace_context,
            workspace_root_project_context=workspace_root_project_context,
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


class TestValidateHelperFile:
    def test_returns_success_when_all_validation_pass(
        self,
        monkeypatch: MonkeyPatch,
    ) -> None:
        # Arrange
        helper_file_path = ProjectRelativePath(Path("src/helpers.py"))
        workspace_context = Mock()
        workspace_root_project_context = Mock()
        project_context = Mock()

        check_mypy = Mock(return_value=Success(Mock(success=True, diagnostics=())))
        check_ruff_lint = Mock(return_value=Success(Mock(success=True, diagnostics=())))

        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.check_file",
            check_mypy,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.check_file_lint",
            check_ruff_lint,
        )

        # Act
        result = _validate_helper_file(
            helper_file_path=helper_file_path,
            workspace_context=workspace_context,
            workspace_root_project_context=workspace_root_project_context,
            project_context=project_context,
        )

        # Assert
        assert result == Success(None)

        check_mypy.assert_called_once_with(
            workspace_relative_file_path=helper_file_path,
            target_project_context=project_context,
            workspace_root_project_context=workspace_root_project_context,
            workspace_context=workspace_context,
        )
        check_ruff_lint.assert_called_once_with(
            workspace_relative_file_path=helper_file_path,
            target_project_context=project_context,
            workspace_root_project_context=workspace_root_project_context,
            workspace_context=workspace_context,
        )

    def test_returns_failure_when_mypy_check_fails(
        self,
        monkeypatch: MonkeyPatch,
    ) -> None:
        # Arrange
        helper_file_path = ProjectRelativePath(Path("src/helpers.py"))
        workspace_context = Mock()
        workspace_root_project_context = Mock()
        project_context = Mock()

        error = create_gyomu_error()
        check_mypy = Mock(return_value=Failure(error))
        check_ruff_lint = Mock()

        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.check_file",
            check_mypy,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.check_file_lint",
            check_ruff_lint,
        )

        # Act
        result = _validate_helper_file(
            helper_file_path=helper_file_path,
            workspace_context=workspace_context,
            workspace_root_project_context=workspace_root_project_context,
            project_context=project_context,
        )

        # Assert
        assert isinstance(result, Failure)
        check_mypy.assert_called_once_with(
            workspace_relative_file_path=helper_file_path,
            target_project_context=project_context,
            workspace_root_project_context=workspace_root_project_context,
            workspace_context=workspace_context,
        )
        check_ruff_lint.assert_not_called()

    def test_returns_failure_when_mypy_validation_fails(
        self,
        monkeypatch: MonkeyPatch,
    ) -> None:
        # Arrange
        helper_file_path = ProjectRelativePath(Path("src/helpers.py"))
        workspace_context = Mock()
        workspace_root_project_context = Mock()
        project_context = Mock()

        diagnostics = ("mypy validation error",)
        check_mypy = Mock(
            return_value=Success(Mock(success=False, diagnostics=diagnostics))
        )
        check_ruff_lint = Mock()

        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.check_file",
            check_mypy,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.check_file_lint",
            check_ruff_lint,
        )

        # Act
        result = _validate_helper_file(
            helper_file_path=helper_file_path,
            workspace_context=workspace_context,
            workspace_root_project_context=workspace_root_project_context,
            project_context=project_context,
        )

        # Assert
        assert isinstance(result, Failure)
        check_mypy.assert_called_once()
        check_ruff_lint.assert_not_called()

    def test_returns_failure_when_ruff_lint_check_fails(
        self,
        monkeypatch: MonkeyPatch,
    ) -> None:
        # Arrange
        helper_file_path = ProjectRelativePath(Path("src/helpers.py"))
        workspace_context = Mock()
        workspace_root_project_context = Mock()
        project_context = Mock()

        check_mypy = Mock(return_value=Success(Mock(success=True, diagnostics=())))
        error = create_gyomu_error()
        check_ruff_lint = Mock(return_value=Failure(error))

        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.check_file",
            check_mypy,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.check_file_lint",
            check_ruff_lint,
        )

        # Act
        result = _validate_helper_file(
            helper_file_path=helper_file_path,
            workspace_context=workspace_context,
            workspace_root_project_context=workspace_root_project_context,
            project_context=project_context,
        )

        # Assert
        assert isinstance(result, Failure)
        check_mypy.assert_called_once()
        check_ruff_lint.assert_called_once_with(
            workspace_relative_file_path=helper_file_path,
            target_project_context=project_context,
            workspace_root_project_context=workspace_root_project_context,
            workspace_context=workspace_context,
        )

    def test_returns_failure_when_ruff_lint_validation_fails(
        self,
        monkeypatch: MonkeyPatch,
    ) -> None:
        # Arrange
        helper_file_path = ProjectRelativePath(Path("src/helpers.py"))
        workspace_context = Mock()
        workspace_root_project_context = Mock()
        project_context = Mock()

        check_mypy = Mock(return_value=Success(Mock(success=True, diagnostics=())))
        diagnostics = ("ruff lint validation error",)
        check_ruff_lint = Mock(
            return_value=Success(Mock(success=False, diagnostics=diagnostics))
        )

        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.check_file",
            check_mypy,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.check_file_lint",
            check_ruff_lint,
        )

        # Act
        result = _validate_helper_file(
            helper_file_path=helper_file_path,
            workspace_context=workspace_context,
            workspace_root_project_context=workspace_root_project_context,
            project_context=project_context,
        )

        # Assert
        assert isinstance(result, Failure)
        check_mypy.assert_called_once()
        check_ruff_lint.assert_called_once_with(
            workspace_relative_file_path=helper_file_path,
            target_project_context=project_context,
            workspace_root_project_context=workspace_root_project_context,
            workspace_context=workspace_context,
        )


class TestCreateHelperInventoryItem:
    def test_returns_success_when_creation_succeeds(
        self,
        monkeypatch: MonkeyPatch,
    ) -> None:
        # Arrange
        item = create_helper_inventory_item()
        workspace_context = Mock()
        workspace_root_project_context = Mock()
        project_context = Mock()
        config_manager = Mock()
        interaction = Mock()

        model_default = create_model_default()
        referenced_types = (Mock(),)
        helper_file_path = ProjectRelativePath(Path("src/helpers.py"))

        resolve_item = Mock(return_value=Success((model_default, referenced_types)))
        update_file = Mock(return_value=Success(helper_file_path))
        format_file_mock = Mock(return_value=Success(None))
        validate_file = Mock(return_value=Success(None))

        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update._resolve_helper_inventory_item",
            resolve_item,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.update_helper_file",
            update_file,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.format_file",
            format_file_mock,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update._validate_helper_file",
            validate_file,
        )

        # Act
        result = _create_helper_inventory_item(
            item=item,
            workspace_context=workspace_context,
            workspace_root_project_context=workspace_root_project_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )

        # Assert
        assert result == Success(None)

        resolve_item.assert_called_once_with(
            item=item,
            workspace_context=workspace_context,
            workspace_root_project_context=workspace_root_project_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )
        update_file.assert_called_once_with(
            item=item,
            workspace_root_project_context=workspace_root_project_context,
            project_context=project_context,
            model_default=model_default,
            referenced_types=referenced_types,
        )
        format_file_mock.assert_called_once_with(
            workspace_relative_file_path=helper_file_path,
            target_project_context=project_context,
            workspace_root_project_context=workspace_root_project_context,
            workspace_context=workspace_context,
        )
        validate_file.assert_called_once_with(
            helper_file_path=helper_file_path,
            workspace_context=workspace_context,
            workspace_root_project_context=workspace_root_project_context,
            project_context=project_context,
        )

    def test_returns_failure_when_resolving_inventory_item_fails(
        self,
        monkeypatch: MonkeyPatch,
    ) -> None:
        # Arrange
        item = create_helper_inventory_item()
        workspace_context = Mock()
        workspace_root_project_context = Mock()
        project_context = Mock()
        config_manager = Mock()
        interaction = Mock()

        error = create_gyomu_error()
        resolve_item = Mock(return_value=Failure(error))
        update_file = Mock()
        format_file_mock = Mock()
        validate_file = Mock()

        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update._resolve_helper_inventory_item",
            resolve_item,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.update_helper_file",
            update_file,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.format_file",
            format_file_mock,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update._validate_helper_file",
            validate_file,
        )

        # Act
        result = _create_helper_inventory_item(
            item=item,
            workspace_context=workspace_context,
            workspace_root_project_context=workspace_root_project_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )

        # Assert
        assert result == Failure(error)
        resolve_item.assert_called_once()
        update_file.assert_not_called()
        format_file_mock.assert_not_called()
        validate_file.assert_not_called()

    def test_returns_failure_when_updating_helper_file_fails(
        self,
        monkeypatch: MonkeyPatch,
    ) -> None:
        # Arrange
        item = create_helper_inventory_item()
        workspace_context = Mock()
        workspace_root_project_context = Mock()
        project_context = Mock()
        config_manager = Mock()
        interaction = Mock()

        model_default = create_model_default()
        referenced_types = (Mock(),)
        error = create_gyomu_test_error()

        resolve_item = Mock(return_value=Success((model_default, referenced_types)))
        update_file = Mock(return_value=Failure(error))
        format_file_mock = Mock()
        validate_file = Mock()

        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update._resolve_helper_inventory_item",
            resolve_item,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.update_helper_file",
            update_file,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.format_file",
            format_file_mock,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update._validate_helper_file",
            validate_file,
        )

        # Act
        result = _create_helper_inventory_item(
            item=item,
            workspace_context=workspace_context,
            workspace_root_project_context=workspace_root_project_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )

        # Assert
        assert isinstance(result, Failure)
        assert result.failure().__cause__ is error
        resolve_item.assert_called_once()
        update_file.assert_called_once_with(
            item=item,
            workspace_root_project_context=workspace_root_project_context,
            project_context=project_context,
            model_default=model_default,
            referenced_types=referenced_types,
        )
        format_file_mock.assert_not_called()
        validate_file.assert_not_called()

    def test_returns_failure_when_formatting_helper_file_fails(
        self,
        monkeypatch: MonkeyPatch,
    ) -> None:
        # Arrange
        item = create_helper_inventory_item()
        workspace_context = Mock()
        workspace_root_project_context = Mock()
        project_context = Mock()
        config_manager = Mock()
        interaction = Mock()

        model_default = create_model_default()
        referenced_types = (Mock(),)
        helper_file_path = ProjectRelativePath(Path("src/helpers.py"))
        error = create_gyomu_error()
        format_error = create_gyomu_error()

        resolve_item = Mock(return_value=Success((model_default, referenced_types)))
        update_file = Mock(return_value=Success(helper_file_path))
        format_file_mock = Mock(return_value=Failure(error))
        wrap_error = Mock(return_value=format_error)
        validate_file = Mock()

        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update._resolve_helper_inventory_item",
            resolve_item,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.update_helper_file",
            update_file,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.format_file",
            format_file_mock,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.wrap_gyomu_error",
            wrap_error,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update._validate_helper_file",
            validate_file,
        )

        # Act
        result = _create_helper_inventory_item(
            item=item,
            workspace_context=workspace_context,
            workspace_root_project_context=workspace_root_project_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )

        # Assert
        assert result == Failure(format_error)
        wrap_error.assert_called_once_with(
            error=error,
            message="fail to format file",
        )
        validate_file.assert_not_called()

    def test_returns_failure_when_validation_fails(
        self,
        monkeypatch: MonkeyPatch,
    ) -> None:
        # Arrange
        item = create_helper_inventory_item()
        workspace_context = Mock()
        workspace_root_project_context = Mock()
        project_context = Mock()
        config_manager = Mock()
        interaction = Mock()

        model_default = create_model_default()
        referenced_types = (Mock(),)
        helper_file_path = ProjectRelativePath(Path("src/helpers.py"))
        error = create_gyomu_error()

        resolve_item = Mock(return_value=Success((model_default, referenced_types)))
        update_file = Mock(return_value=Success(helper_file_path))
        format_file_mock = Mock(return_value=Success(None))
        validate_file = Mock(return_value=Failure(error))

        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update._resolve_helper_inventory_item",
            resolve_item,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.update_helper_file",
            update_file,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update.format_file",
            format_file_mock,
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update._validate_helper_file",
            validate_file,
        )

        # Act
        result = _create_helper_inventory_item(
            item=item,
            workspace_context=workspace_context,
            workspace_root_project_context=workspace_root_project_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )

        # Assert
        assert result == Failure(error)
        validate_file.assert_called_once_with(
            helper_file_path=helper_file_path,
            workspace_context=workspace_context,
            workspace_root_project_context=workspace_root_project_context,
            project_context=project_context,
        )


class TestCreateHelperInventory:
    def test_empty_create_returns_success(self) -> None:
        # Arrange
        workspace_context = Mock()
        workspace_root_project_context = Mock()
        project_context = Mock()
        config_manager = Mock()
        interaction = Mock()

        # Act
        result = _create_helper_inventory(
            create=(),
            workspace_context=workspace_context,
            workspace_root_project_context=workspace_root_project_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )

        # Assert
        assert isinstance(result, Success)

    def test_returns_success_when_all_items_are_created(
        self,
        monkeypatch: MonkeyPatch,
    ) -> None:
        # Arrange
        items = (
            create_helper_inventory_item(),
            create_helper_inventory_item(),
        )
        workspace_context = Mock()
        workspace_root_project_context = Mock()
        project_context = Mock()
        config_manager = Mock()
        interaction = Mock()

        create_item = Mock(return_value=Success(None))
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update._create_helper_inventory_item",
            create_item,
        )

        # Act
        result = _create_helper_inventory(
            create=items,
            workspace_context=workspace_context,
            workspace_root_project_context=workspace_root_project_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )

        # Assert
        assert result == Success(None)
        assert create_item.call_count == 2
        create_item.assert_any_call(
            item=items[0],
            workspace_context=workspace_context,
            workspace_root_project_context=workspace_root_project_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )
        create_item.assert_any_call(
            item=items[1],
            workspace_context=workspace_context,
            workspace_root_project_context=workspace_root_project_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )

    def test_returns_failure_and_stops_processing_when_item_creation_fails(
        self,
        monkeypatch: MonkeyPatch,
    ) -> None:
        # Arrange
        items = (
            create_helper_inventory_item(),
            create_helper_inventory_item(),
            create_helper_inventory_item(),
        )
        workspace_context = Mock()
        workspace_root_project_context = Mock()
        project_context = Mock()
        config_manager = Mock()
        interaction = Mock()

        error = create_gyomu_error()
        create_item = Mock(
            side_effect=[
                Success(None),
                Failure(error),
            ]
        )
        monkeypatch.setattr(
            "gyomu_workflow.test.helpers.update._create_helper_inventory_item",
            create_item,
        )

        # Act
        result = _create_helper_inventory(
            create=items,
            workspace_context=workspace_context,
            workspace_root_project_context=workspace_root_project_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )

        # Assert
        assert result == Failure(error)
        assert create_item.call_count == 2
        create_item.assert_any_call(
            item=items[0],
            workspace_context=workspace_context,
            workspace_root_project_context=workspace_root_project_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )
        create_item.assert_any_call(
            item=items[1],
            workspace_context=workspace_context,
            workspace_root_project_context=workspace_root_project_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
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
        workspace_root_project_context = create_project_context()
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
        mocker.patch.object(
            helpers_module,
            "initialize_project_context",
            return_value=Success(workspace_root_project_context),
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
            workspace_root_project_context=workspace_root_project_context,
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
