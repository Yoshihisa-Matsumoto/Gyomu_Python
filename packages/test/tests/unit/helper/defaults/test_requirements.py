from dataclasses import dataclass, replace
from pathlib import Path

import pytest
from gyomu_config.manager import ConfigManager
from gyomu_python_analysis.analysis.initialize import initialize_project_context
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_schema.schemas.python.types import ProjectRelativePath, PythonPath
from gyomu_schema.schemas.testing.helper import HelperInventoryItem
from gyomu_schema.schemas.types import FullPath
from gyomu_schema.utility.fromatting import format_object
from gyomu_test.error.test import GyomuTestError
from gyomu_test.helper.defaults.requirements import (
    ConfiguredParameterDefault,
    MissingParameterDefault,
    ResolvedParameterDefault,
    resolve_function_parameter_defaults,
)
from gyomu_test.helper.inventory.expected import collect_model_helper_inventory
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.python_analysis.test_support.helpers import (
    create_analysis_error,
    create_primitive_type,
    create_resolve_error,
    create_symbol_type,
)
from packages.schema.test_support.helpers import (
    create_call_parameter,
    create_class_analysis,
    create_file_analysis_context,
    create_list_parameter,
    create_literal_parameter,
    create_module_analysis,
    create_none_parameter,
    create_tuple_parameter,
    create_type_analysis,
    simple_create_declaration_identity,
)
from packages.schema.test_support.testing_helpers import create_parameter_info
from packages.test.test_support.helpers import (
    MONOREPO_FIXTURES_ROOT,
    create_missing_parameter_default,
    create_resolved_parameter_default,
)
from packages.test.tests.unit.helper.helpers import (
    create_gyomu_test_error,
    get_project_context,
    get_workspace_context,
    validate_parameters,
)


@dataclass
class HelperInventoryTestContext:
    workspace_context: WorkspaceContext
    project_context: ProjectContext
    config_manager: ConfigManager


@pytest.fixture
def helper_inventory_test_context() -> HelperInventoryTestContext:
    target_path = FullPath(MONOREPO_FIXTURES_ROOT)
    workspace_context = get_workspace_context(target_path)

    project_context = get_project_context(workspace_context, "parameter")

    config_manager = ConfigManager()

    root_context_result = initialize_project_context(
        project_root=workspace_context.workspace_root.path,
        source_root=ProjectRelativePath(Path(".")),
    )
    assert isinstance(root_context_result, Success)

    return HelperInventoryTestContext(
        workspace_context=workspace_context,
        project_context=project_context,
        config_manager=config_manager,
    )


def get_inventory(
    inventories: tuple[HelperInventoryItem, ...], name: str
) -> HelperInventoryItem:
    return next(
        inventory
        for inventory in inventories
        if inventory.target_identity.get_symbol_name() == name
    )


class TestResolveFunctionParameterDefaults:
    def test_with_function_parameter_default(
        self,
        helper_inventory_test_context: HelperInventoryTestContext,
        mocker: MockerFixture,
    ) -> None:
        context = helper_inventory_test_context

        result = collect_model_helper_inventory(
            context.project_context, context.workspace_context
        )
        assert isinstance(result, Success)
        inventories = result.unwrap()
        inventory = get_inventory(inventories, "StringLiteralModel")

        result = resolve_function_parameter_defaults(
            inventory=inventory,
            workspace_context=context.workspace_context,
            project_context=context.project_context,
            config_manager=context.config_manager,
        )

        assert isinstance(result, Success)

        parameters = result.unwrap()
        print(format_object(parameters, depth=8))

        for parameter in parameters:
            assert isinstance(parameter, ConfiguredParameterDefault)
            assert parameter.parameter.name == "value"
            default = parameter.parameter.default
            assert default

    @pytest.mark.parametrize(
        ("model_name", "expected_result"),
        [
            (
                "StringLiteralModel",
                (
                    create_missing_parameter_default(
                        parameter=create_parameter_info(name="value"),
                        missing_types=(
                            create_primitive_type(
                                parameter_name="value", primitive_type="str"
                            ),
                        ),
                    ),
                ),
            ),
            (
                "CallDefaultModel",
                (
                    create_resolved_parameter_default(
                        parameter=create_parameter_info(name="value"),
                        default=create_call_parameter(
                            callable_identity=simple_create_declaration_identity(
                                id="packages.parameter.test_support.helpers::create_basic_model"
                            )
                        ),
                    ),
                ),
            ),
            (
                "IntegerLiteralModel",
                (
                    create_resolved_parameter_default(
                        parameter=create_parameter_info(name="value"),
                        default=create_literal_parameter(value=9),
                    ),
                ),
            ),
            (
                "BooleanLiteralModel",
                (
                    create_missing_parameter_default(
                        parameter=create_parameter_info(name="value"),
                        missing_types=(
                            create_primitive_type(
                                parameter_name="value", primitive_type="bool"
                            ),
                        ),
                    ),
                ),
            ),
            (
                "NoneDefaultModel",
                (
                    create_resolved_parameter_default(
                        parameter=create_parameter_info(name="value"),
                        default=create_none_parameter(),
                    ),
                ),
            ),
            (
                "NameReferenceModel",
                (
                    create_missing_parameter_default(
                        parameter=create_parameter_info(name="value"),
                        missing_types=(
                            create_primitive_type(
                                parameter_name="value", primitive_type="str"
                            ),
                        ),
                    ),
                ),
            ),
            (
                "AttributeReferenceModel",
                (
                    create_missing_parameter_default(
                        parameter=create_parameter_info(name="value"),
                        missing_types=(
                            create_symbol_type(
                                symbol=create_class_analysis(name="Color"),
                                context=create_file_analysis_context(
                                    analysis=create_module_analysis(
                                        module_name=PythonPath("parameter.models")
                                    )
                                ),
                            ),
                        ),
                    ),
                ),
            ),
            (
                "TupleLiteralModel",
                (
                    create_resolved_parameter_default(
                        parameter=create_parameter_info(name="value"),
                        default=create_tuple_parameter(
                            elements=(create_literal_parameter(value=9),)
                        ),
                    ),
                ),
            ),
            (
                "EmptyTupleModel",
                (
                    create_missing_parameter_default(
                        parameter=create_parameter_info(name="value"),
                        missing_types=(
                            create_primitive_type(
                                parameter_name="value", primitive_type="str"
                            ),
                        ),
                    ),
                ),
            ),
            (
                "ListLiteralModel",
                (
                    create_resolved_parameter_default(
                        parameter=create_parameter_info(name="value"),
                        default=create_list_parameter(
                            elements=(create_literal_parameter(value=9),)
                        ),
                    ),
                ),
            ),
            (
                "DictLiteralModel",
                (
                    create_missing_parameter_default(
                        parameter=create_parameter_info(name="value"),
                        missing_types=(
                            create_primitive_type(
                                parameter_name="value", primitive_type="str"
                            ),
                        ),
                    ),
                ),
            ),
        ],
    )
    def test_parameter(
        self,
        helper_inventory_test_context: HelperInventoryTestContext,
        mocker: MockerFixture,
        model_name: str,
        expected_result: tuple[ResolvedParameterDefault | MissingParameterDefault, ...],
    ) -> None:
        context = helper_inventory_test_context

        mocker.patch(
            "gyomu_test.helper.inventory.expected.retrieve_config",
            return_value=Success(None),
        )
        inventory_result = collect_model_helper_inventory(
            context.project_context, context.workspace_context
        )
        assert isinstance(inventory_result, Success)
        inventories = inventory_result.unwrap()
        inventory = get_inventory(inventories, model_name)

        result = resolve_function_parameter_defaults(
            inventory=inventory,
            workspace_context=context.workspace_context,
            project_context=context.project_context,
            config_manager=context.config_manager,
        )

        assert isinstance(result, Success)

        parameters = result.unwrap()
        validate_parameters(result=parameters, expected=expected_result)

    def test_str_text_parameter(
        self,
        helper_inventory_test_context: HelperInventoryTestContext,
        mocker: MockerFixture,
    ) -> None:
        context = helper_inventory_test_context

        mocker.patch(
            "gyomu_test.helper.inventory.expected.retrieve_config",
            return_value=Success(None),
        )
        inventory_result = collect_model_helper_inventory(
            context.project_context, context.workspace_context
        )
        assert isinstance(inventory_result, Success)
        inventories = inventory_result.unwrap()
        inventory = get_inventory(inventories, "StringLiteralModel")
        fake_type = create_type_analysis(text="str")
        inventory = replace(
            inventory,
            parameters=(
                replace(
                    inventory.parameters[0],
                    parameter_type=fake_type,
                ),
            ),
        )
        result = resolve_function_parameter_defaults(
            inventory=inventory,
            workspace_context=context.workspace_context,
            project_context=context.project_context,
            config_manager=context.config_manager,
        )

        assert isinstance(result, Success)

        parameters = result.unwrap()
        expected_result: tuple[
            ResolvedParameterDefault | MissingParameterDefault, ...
        ] = (
            create_missing_parameter_default(
                parameter=create_parameter_info(name="value"),
                missing_types=(
                    create_primitive_type(parameter_name="value", primitive_type="str"),
                ),
            ),
        )
        validate_parameters(result=parameters, expected=expected_result)

    def test_int_text_parameter(
        self,
        helper_inventory_test_context: HelperInventoryTestContext,
        mocker: MockerFixture,
    ) -> None:
        context = helper_inventory_test_context

        mocker.patch(
            "gyomu_test.helper.inventory.expected.retrieve_config",
            return_value=Success(None),
        )
        inventory_result = collect_model_helper_inventory(
            context.project_context, context.workspace_context
        )
        assert isinstance(inventory_result, Success)
        inventories = inventory_result.unwrap()
        inventory = get_inventory(inventories, "IntegerLiteralModel")
        fake_type = create_type_analysis(text="int")
        inventory = replace(
            inventory,
            parameters=(
                replace(
                    inventory.parameters[0],
                    parameter_type=fake_type,
                ),
            ),
        )
        result = resolve_function_parameter_defaults(
            inventory=inventory,
            workspace_context=context.workspace_context,
            project_context=context.project_context,
            config_manager=context.config_manager,
        )

        assert isinstance(result, Success)

        parameters = result.unwrap()
        expected_result: tuple[
            ResolvedParameterDefault | MissingParameterDefault, ...
        ] = (
            create_resolved_parameter_default(
                parameter=create_parameter_info(name="value"),
                default=create_literal_parameter(value=9),
            ),
        )
        validate_parameters(result=parameters, expected=expected_result)

    def test_file_analysis_failure(
        self,
        helper_inventory_test_context: HelperInventoryTestContext,
        mocker: MockerFixture,
    ) -> None:
        context = helper_inventory_test_context

        mocker.patch(
            "gyomu_test.helper.inventory.expected.retrieve_config",
            return_value=Success(None),
        )
        inventory_result = collect_model_helper_inventory(
            context.project_context, context.workspace_context
        )
        assert isinstance(inventory_result, Success)
        inventories = inventory_result.unwrap()
        inventory = get_inventory(inventories, "IntegerLiteralModel")

        expected_error = create_analysis_error(
            message="test error",
        )

        mocker.patch.object(
            context.workspace_context,
            "find_file_analysis_context",
            return_value=Failure(expected_error),
        )

        result = resolve_function_parameter_defaults(
            inventory=inventory,
            workspace_context=context.workspace_context,
            project_context=context.project_context,
            config_manager=context.config_manager,
        )

        assert isinstance(result, Failure)
        assert result.failure().message == "fail to get file analysis"

    def test_get_model_kind_failure(
        self,
        helper_inventory_test_context: HelperInventoryTestContext,
        mocker: MockerFixture,
    ) -> None:
        context = helper_inventory_test_context
        mocker.patch(
            "gyomu_test.helper.inventory.expected.retrieve_config",
            return_value=Success(None),
        )
        inventory_result = collect_model_helper_inventory(
            context.project_context, context.workspace_context
        )
        assert isinstance(inventory_result, Success)
        inventories = inventory_result.unwrap()
        inventory = get_inventory(inventories, "CallDefaultModel")

        expected_error = create_resolve_error(message="test error")

        mocker.patch(
            "gyomu_test.helper.defaults.requirements._get_model_kind",
            return_value=Failure(expected_error),
        )

        result = resolve_function_parameter_defaults(
            inventory=inventory,
            workspace_context=context.workspace_context,
            project_context=context.project_context,
            config_manager=context.config_manager,
        )

        assert isinstance(result, Failure)
        failure = result.failure()
        assert isinstance(failure, GyomuTestError)
        assert failure.__cause__ == expected_error

    def test_find_workspace_project_failure(
        self,
        helper_inventory_test_context: HelperInventoryTestContext,
        mocker: MockerFixture,
    ) -> None:
        context = helper_inventory_test_context
        mocker.patch(
            "gyomu_test.helper.inventory.expected.retrieve_config",
            return_value=Success(None),
        )
        inventory_result = collect_model_helper_inventory(
            context.project_context, context.workspace_context
        )
        assert isinstance(inventory_result, Success)
        inventories = inventory_result.unwrap()
        inventory = get_inventory(inventories, "CallDefaultModel")

        expected_error = create_resolve_error(message="test error")

        mocker.patch(
            "gyomu_test.helper.defaults.requirements.find_workspace_project",
            return_value=Failure(expected_error),
        )

        result = resolve_function_parameter_defaults(
            inventory=inventory,
            workspace_context=context.workspace_context,
            project_context=context.project_context,
            config_manager=context.config_manager,
        )

        assert isinstance(result, Failure)
        failure = result.failure()
        assert isinstance(failure, GyomuTestError)
        assert failure.__cause__ == expected_error

    def test_load_symbol_parameter_default_config_failure(
        self,
        helper_inventory_test_context: HelperInventoryTestContext,
        mocker: MockerFixture,
    ) -> None:
        context = helper_inventory_test_context
        mocker.patch(
            "gyomu_test.helper.inventory.expected.retrieve_config",
            return_value=Success(None),
        )
        inventory_result = collect_model_helper_inventory(
            context.project_context, context.workspace_context
        )
        assert isinstance(inventory_result, Success)
        inventories = inventory_result.unwrap()
        inventory = get_inventory(inventories, "AttributeReferenceModel")

        expected_error = create_gyomu_test_error(message="test error")

        mocker.patch(
            "gyomu_test.helper.defaults.requirements.load_symbol_parameter_default_config",
            return_value=Failure(expected_error),
        )

        result = resolve_function_parameter_defaults(
            inventory=inventory,
            workspace_context=context.workspace_context,
            project_context=context.project_context,
            config_manager=context.config_manager,
        )

        assert isinstance(result, Failure)
        failure = result.failure()
        assert isinstance(failure, GyomuTestError)
        assert failure is expected_error

    def test_load_primitive_parameter_default_config_failure(
        self,
        helper_inventory_test_context: HelperInventoryTestContext,
        mocker: MockerFixture,
    ) -> None:
        context = helper_inventory_test_context
        mocker.patch(
            "gyomu_test.helper.inventory.expected.retrieve_config",
            return_value=Success(None),
        )
        inventory_result = collect_model_helper_inventory(
            context.project_context, context.workspace_context
        )
        assert isinstance(inventory_result, Success)
        inventories = inventory_result.unwrap()
        inventory = get_inventory(inventories, "IntegerLiteralModel")

        expected_error = create_gyomu_test_error(message="test error")

        mocker.patch(
            "gyomu_test.helper.defaults.requirements.load_primitive_parameter_default_config",
            return_value=Failure(expected_error),
        )

        result = resolve_function_parameter_defaults(
            inventory=inventory,
            workspace_context=context.workspace_context,
            project_context=context.project_context,
            config_manager=context.config_manager,
        )

        assert isinstance(result, Failure)
        failure = result.failure()
        assert isinstance(failure, GyomuTestError)
        assert failure is expected_error
