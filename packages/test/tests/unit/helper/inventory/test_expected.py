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


def get_project_context(
    workspace_context: WorkspaceContext, project_name: str
) -> ProjectContext:
    project = next(
        (
            project
            for project in workspace_context.projects
            if project.config.name == project_name
        ),
        None,
    )
    assert project is not None
    return initialize_project_from_workspace(
        workspace_path=workspace_context.path, project=project
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


def inventory_not_exist(
    inventories: tuple[HelperInventoryItem, ...], symbol_id: str
) -> None:
    target_inventory = next(
        (
            inventory
            for inventory in inventories
            if str(inventory.target_identity.symbol_id) == symbol_id
        ),
        None,
    )
    assert target_inventory is None


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
    def test_build_from_fixture(self, workspace_context: WorkspaceContext) -> None:
        project_context = get_project_context(workspace_context, "project-b")
        result = collect_model_helper_inventory(project_context, workspace_context)

        assert isinstance(result, Success)
        inventories = result.unwrap()

        equal_helper_inventory(
            inventories,
            symbol_id="project_b.models::ProductBaseModel",
            function_name="create_product_base_model",
            parameters=(
                ParameterSummary(name="product_id", parameter_type="int"),
                ParameterSummary(name="name", parameter_type="str"),
            ),
        )
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

        inventory_not_exist(
            inventories=inventories,
            symbol_id="project_b.non_models::ProductBaseModel",
        )

        inventory_not_exist(
            inventories=inventories,
            symbol_id="project_b.non_models::ProductModel",
        )

        inventory_not_exist(
            inventories=inventories,
            symbol_id="project_b.non_models::NonHelper",
        )

        inventory_not_exist(
            inventories=inventories,
            symbol_id="project_b.inheritance::NonTarget",
        )

        equal_helper_inventory(
            inventories,
            symbol_id="project_b.inheritance::AnotherBase",
            function_name="create_another_base",
            parameters=(),
        )

        equal_helper_inventory(
            inventories,
            symbol_id="project_b.inheritance::ProductAudit",
            function_name="create_product_audit",
            parameters=(ParameterSummary(name="created_by", parameter_type="str"),),
        )

        equal_helper_inventory(
            inventories,
            symbol_id="project_b.inheritance::AuditedProduct",
            function_name="create_audited_product",
            parameters=(
                ParameterSummary(name="created_by", parameter_type="str"),
                ParameterSummary(name="audited", parameter_type="bool"),
            ),
        )

        equal_helper_inventory(
            inventories,
            symbol_id="project_b.inheritance::MultipleProduct",
            function_name="create_multiple_product",
            parameters=(
                ParameterSummary(name="created_by", parameter_type="str"),
                ParameterSummary(name="audited", parameter_type="bool"),
                ParameterSummary(name="product_id", parameter_type="int"),
                ParameterSummary(name="name", parameter_type="str"),
                ParameterSummary(name="multi_name", parameter_type="str"),
            ),
        )
