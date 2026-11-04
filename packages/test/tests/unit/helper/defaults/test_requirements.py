from dataclasses import dataclass
from pathlib import Path

import pytest
from gyomu_config.manager import ConfigManager
from gyomu_python_analysis.analysis.initialize import initialize_project_context
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import WorkspaceContext, WorkspaceRoot
from gyomu_python_analysis.resolve.file_analysis_cache import FileAnalysisCache
from gyomu_schema.schemas.config.test.model_defaults import (
    CallParameter,
    LiteralParameter,
)
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.schemas.testing.helper import HelperInventoryItem
from gyomu_schema.schemas.types import FullPath
from gyomu_schema.utility.fromatting import format_object
from gyomu_test.helper.defaults.requirements import (
    ConfiguredParameterDefault,
    MissingParameterDefault,
    ResolvedParameterDefault,
    resolve_function_parameter_defaults,
)
from gyomu_test.helper.inventory.expected import collect_model_helper_inventory
from pytest_mock import MockerFixture
from returns.result import Success

from packages.test.test_support.helpers import MONOREPO_FIXTURES_ROOT
from packages.test.tests.unit.helper.helpers import (
    get_project_context,
    get_workspace_context,
)


@dataclass
class HelperInventoryTestContext:
    workspace_root: WorkspaceRoot
    workspace_context: WorkspaceContext
    project_context: ProjectContext
    file_analysis_cache: FileAnalysisCache
    config_manager: ConfigManager


@pytest.fixture
def helper_inventory_test_context() -> HelperInventoryTestContext:
    target_path = FullPath(MONOREPO_FIXTURES_ROOT)
    workspace_root, workspace_context = get_workspace_context(target_path)

    project_context = get_project_context(workspace_context, "parameter")

    file_analysis_cache = FileAnalysisCache(workspace_context=workspace_context)

    config_manager = ConfigManager()

    root_context_result = initialize_project_context(
        project_root=workspace_context.path,
        source_root=ProjectRelativePath(Path(".")),
    )
    assert isinstance(root_context_result, Success)

    return HelperInventoryTestContext(
        workspace_root=workspace_root,
        workspace_context=workspace_context,
        project_context=project_context,
        file_analysis_cache=file_analysis_cache,
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
            workspace_root=context.workspace_root,
            workspace_context=context.workspace_context,
            project_context=context.project_context,
            file_analysis_cache=context.file_analysis_cache,
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

    def test_without_default(
        self,
        helper_inventory_test_context: HelperInventoryTestContext,
        mocker: MockerFixture,
    ) -> None:
        context = helper_inventory_test_context

        with mocker.patch(
            "gyomu_test.helper.inventory.expected.retrieve_config",
            return_value=Success(None),
        ):
            inventory_result = collect_model_helper_inventory(
                context.project_context, context.workspace_context
            )
        assert isinstance(inventory_result, Success)
        inventories = inventory_result.unwrap()
        inventory = get_inventory(inventories, "StringLiteralModel")

        result = resolve_function_parameter_defaults(
            inventory=inventory,
            workspace_root=context.workspace_root,
            workspace_context=context.workspace_context,
            project_context=context.project_context,
            file_analysis_cache=context.file_analysis_cache,
            config_manager=context.config_manager,
        )

        assert isinstance(result, Success)

        parameters = result.unwrap()
        print(format_object(parameters, depth=8))

        for parameter in parameters:
            assert isinstance(parameter, MissingParameterDefault)
            assert parameter.parameter.name == "value"
            default = parameter.parameter.default
            assert default is None

    def test_with_helper_candidate_menber(
        self,
        helper_inventory_test_context: HelperInventoryTestContext,
        mocker: MockerFixture,
    ) -> None:
        context = helper_inventory_test_context

        with mocker.patch(
            "gyomu_test.helper.inventory.expected.retrieve_config",
            return_value=Success(None),
        ):
            inventory_result = collect_model_helper_inventory(
                context.project_context, context.workspace_context
            )
        assert isinstance(inventory_result, Success)
        inventories = inventory_result.unwrap()
        inventory = get_inventory(inventories, "CallDefaultModel")

        result = resolve_function_parameter_defaults(
            inventory=inventory,
            workspace_root=context.workspace_root,
            workspace_context=context.workspace_context,
            project_context=context.project_context,
            file_analysis_cache=context.file_analysis_cache,
            config_manager=context.config_manager,
        )

        assert isinstance(result, Success)

        parameters = result.unwrap()
        print(format_object(parameters))

        for parameter in parameters:
            assert isinstance(parameter, ResolvedParameterDefault)
            assert parameter.parameter.name == "value"
            default = parameter.default
            assert default is not None
            assert isinstance(default, CallParameter)
            assert default.callable_identity.get_symbol_name() == "create_basic_model"

    def test_with_int_parameter(
        self,
        helper_inventory_test_context: HelperInventoryTestContext,
        mocker: MockerFixture,
    ) -> None:
        context = helper_inventory_test_context

        with mocker.patch(
            "gyomu_test.helper.inventory.expected.retrieve_config",
            return_value=Success(None),
        ):
            inventory_result = collect_model_helper_inventory(
                context.project_context, context.workspace_context
            )
        assert isinstance(inventory_result, Success)
        inventories = inventory_result.unwrap()
        inventory = get_inventory(inventories, "IntegerLiteralModel")

        result = resolve_function_parameter_defaults(
            inventory=inventory,
            workspace_root=context.workspace_root,
            workspace_context=context.workspace_context,
            project_context=context.project_context,
            file_analysis_cache=context.file_analysis_cache,
            config_manager=context.config_manager,
        )

        assert isinstance(result, Success)

        parameters = result.unwrap()
        print(format_object(parameters, depth=8))

        for parameter in parameters:
            assert isinstance(parameter, ResolvedParameterDefault)
            assert parameter.parameter.name == "value"
            default = parameter.default
            assert default is not None
            assert isinstance(default, LiteralParameter)
            assert default.value == 9
