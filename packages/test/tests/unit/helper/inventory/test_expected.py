from pathlib import Path

from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_python_analysis.project.workspace import (
    WorkspaceContext,
)
from gyomu_schema.schemas.python.types import (
    DeclarationId,
    DeclarationIdentity,
    ProjectRelativePath,
    PythonPath,
    SymbolId,
)
from gyomu_schema.utility.fromatting import format_object
from gyomu_test.error.inventory import ProjectInventoryError
from gyomu_test.error.test import TestError
from gyomu_test.helper.inventory.expected import collect_model_helper_inventory
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.test.tests.unit.helper.inventory.helpers import (
    ParameterSummary,
    equal_helper_inventory,
    error_contains_missing_type_annotation,
    get_project_context,
    inventory_not_exist,
)


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
                ParameterSummary(name="product_id", parameter_type="int", default=None),
                ParameterSummary(name="name", parameter_type="str", default=None),
            ),
        )
        equal_helper_inventory(
            inventories,
            symbol_id="project_b.models::ProductModel",
            function_name="create_product_model",
            parameters=(
                ParameterSummary(name="product_id", parameter_type="int", default=None),
                ParameterSummary(name="name", parameter_type="str", default=None),
                ParameterSummary(name="price", parameter_type="float", default=None),
            ),
        )
        equal_helper_inventory(
            inventories,
            symbol_id="project_b.models::ProductSummary",
            function_name="create_product_summary",
            parameters=(
                ParameterSummary(name="product_id", parameter_type="int", default=None),
                ParameterSummary(
                    name="display_name", parameter_type="str", default=None
                ),
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

    def test_missing_type_annotation(self, workspace_context: WorkspaceContext) -> None:
        project_context = get_project_context(workspace_context, "project-a")
        result = collect_model_helper_inventory(project_context, workspace_context)

        assert isinstance(result, Failure)
        failure = result.failure()
        assert isinstance(failure, ProjectInventoryError)
        print(format_object(failure, depth=7))
        error_contains_missing_type_annotation(
            failure=failure,
            file_path=ProjectRelativePath(Path("src/project_a/invalid_models.py")),
            identity=DeclarationIdentity(
                symbol_id=SymbolId("project_a.invalid_models::InvalidModel"),
                declaration_id=DeclarationId(".::user_id"),
            ),
        )
        error_contains_missing_type_annotation(
            failure=failure,
            file_path=ProjectRelativePath(Path("src/project_a/invalid_models.py")),
            identity=DeclarationIdentity(
                symbol_id=SymbolId("project_a.invalid_models::InvalidModel"),
                declaration_id=DeclarationId(".::address"),
            ),
        )

    def test_returns_test_error_when_file_loading_fails(
        self,
        workspace_context: WorkspaceContext,
        mocker: MockerFixture,
    ) -> None:
        project_context = get_project_context(workspace_context, "project-b")
        analysis_error = AnalysisError(
            message="test",
            file_path=PythonPath("gyomu_test.test"),
            phase="workspace-discovery",
        )

        load_mock = mocker.patch(
            "gyomu_test.helper.inventory.expected.load_file_analysis_context",
            return_value=Failure(analysis_error),
        )

        result = collect_model_helper_inventory(project_context, workspace_context)

        assert isinstance(result, Failure)
        fail = result.failure()
        assert isinstance(fail, TestError)
        assert fail.__cause__ is analysis_error
        load_mock.assert_called_once()

    def test_returns_test_error_when_basemodel_check_fails(
        self,
        workspace_context: WorkspaceContext,
        mocker: MockerFixture,
    ) -> None:
        project_context = get_project_context(workspace_context, "project-b")
        analysis_error = AnalysisError(
            message="test",
            file_path=PythonPath("gyomu_test.test"),
            phase="workspace-discovery",
        )

        inherits_mock = mocker.patch(
            "gyomu_test.helper.inventory.expected.inherits_from_pydantic_basemodel",
            return_value=Failure(analysis_error),
        )

        result = collect_model_helper_inventory(project_context, workspace_context)

        assert isinstance(result, Failure)
        fail = result.failure()
        assert isinstance(fail, TestError)
        assert fail.__cause__ is analysis_error
        inherits_mock.assert_called_once()

    def test_returns_test_error_when_class_hierarchy_fails(
        self,
        workspace_context: WorkspaceContext,
        mocker: MockerFixture,
    ) -> None:
        project_context = get_project_context(workspace_context, "project-b")
        analysis_error = AnalysisError(
            message="test",
            file_path=PythonPath("gyomu_test.test"),
            phase="workspace-discovery",
        )

        hierarchy_mock = mocker.patch(
            "gyomu_test.helper.inventory.expected.collect_class_hierarchy",
            return_value=Failure(analysis_error),
        )

        result = collect_model_helper_inventory(project_context, workspace_context)

        assert isinstance(result, Failure)
        fail = result.failure()
        assert isinstance(fail, TestError)
        assert fail.__cause__ is analysis_error
        hierarchy_mock.assert_called_once()
