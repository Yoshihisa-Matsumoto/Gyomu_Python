from dataclasses import dataclass

import pytest
from gyomu_python_analysis.analysis.initialize import initialize_project_from_workspace
from gyomu_python_analysis.analysis.workspace import initialize_workspace_context
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import (
    WorkspaceContext,
    WorkspaceRoot,
    WorkspaceRootKind,
)
from gyomu_schema.schemas.testing.helper import HelperInventoryItem, ParameterInfo
from gyomu_test.helper.inventory.expected import collect_model_helper_inventory
from returns.result import Success

from packages.test.test_support.helpers import MONOREPO_FIXTURES_ROOT


@pytest.fixture
def workspace_context() -> WorkspaceContext:
    result = initialize_workspace_context(
        root=WorkspaceRoot(
            path=MONOREPO_FIXTURES_ROOT,
            kind=WorkspaceRootKind.UV_WORKSPACE,
        )
    )
    assert isinstance(result, Success)
    return result.unwrap()


@pytest.fixture
def project_b_context(workspace_context: WorkspaceContext) -> ProjectContext:
    project_b = next(
        (
            project
            for project in workspace_context.projects
            if project.config.name == "project-b"
        ),
        None,
    )
    assert project_b is not None
    return initialize_project_from_workspace(
        workspace_path=workspace_context.path, project=project_b
    )


@dataclass
class ParameterSummary:
    name: str
    parameter_type: str


def equal_helper_inventory_parameter(
    parameters: tuple[ParameterInfo, ...], parameter_name: str, parameter_type: str
) -> None:
    target_parameter = next(
        (parameter for parameter in parameters if parameter.name == parameter_name),
        None,
    )
    assert target_parameter is not None
    assert target_parameter.parameter_type.text == parameter_type


def equal_helper_inventory(
    inventories: tuple[HelperInventoryItem, ...],
    symbol_id: str,
    function_name: str,
    parameters: tuple[ParameterSummary, ...],
) -> None:
    target_inventory = next(
        (
            inventory
            for inventory in inventories
            if inventory.function_name == function_name
        ),
        None,
    )
    assert target_inventory is not None
    assert str(target_inventory.target_identity.symbol_id) == symbol_id

    for parameter in parameters:
        equal_helper_inventory_parameter(
            target_inventory.parameters,
            parameter_name=parameter.name,
            parameter_type=parameter.parameter_type,
        )
    actual_parameters = {
        parameter.name: parameter.parameter_type.text
        for parameter in target_inventory.parameters
    }
    expected_parameters = {
        parameter.name: parameter.parameter_type for parameter in parameters
    }

    assert actual_parameters == expected_parameters


class TestCollectModelHelperInventory:
    def test_build_from_fixture(
        self, workspace_context: WorkspaceContext, project_b_context: ProjectContext
    ) -> None:
        result = collect_model_helper_inventory(project_b_context, workspace_context)

        assert isinstance(result, Success)
        inventories = result.unwrap()
        print(inventories)

        equal_helper_inventory(
            inventories,
            symbol_id="project_b.models::ProductModel",
            function_name="create_product_model",
            parameters=(
                ParameterSummary(name="product_id", parameter_type="int"),
                ParameterSummary(name="name", parameter_type="str"),
                ParameterSummary(name="price", parameter_type="float"),
            ),
        )
        equal_helper_inventory(
            inventories,
            symbol_id="project_b.models::ProductSummary",
            function_name="create_product_summary",
            parameters=(
                ParameterSummary(name="product_id", parameter_type="int"),
                ParameterSummary(name="display_name", parameter_type="str"),
            ),
        )
