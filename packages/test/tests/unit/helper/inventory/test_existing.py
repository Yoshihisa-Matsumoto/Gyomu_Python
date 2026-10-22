from pathlib import Path

from gyomu_python_analysis.analysis.initialize import initialize_project_context
from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_schema.schemas.python.types import ProjectRelativePath, PythonPath
from gyomu_schema.utility.fromatting import format_object
from gyomu_test.error.inventory import ProjectInventoryError
from gyomu_test.helper.inventory.existing import collect_existing_helper_inventory
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.test.tests.unit.helper.inventory.helpers import (
    ParameterSummary,
    equal_helper_inventory,
    error_contains_function_reference_error,
    error_contains_missing_parameter_type_annotation,
    error_contains_missing_return_type_annotation,
    function_not_exist_in_inventory,
    get_project_context,
)


class TestCollectExistingHelperInventory:
    def test_build_from_fixture(self, workspace_context: WorkspaceContext) -> None:
        project_context = get_project_context(workspace_context, "project-b")
        root_context_result = initialize_project_context(
            project_root=workspace_context.path,
            source_root=ProjectRelativePath(Path(".")),
        )
        assert isinstance(root_context_result, Success)

        result = collect_existing_helper_inventory(
            root=root_context_result.unwrap(), target_project=project_context
        )
        assert isinstance(result, Success)
        inventories = result.unwrap()

        print(inventories)
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
            symbol_id="project_b.models::ProductSummary",
            function_name="create_product_summary",
            parameters=(
                ParameterSummary(name="product_id", parameter_type="int"),
                ParameterSummary(name="display_name", parameter_type="str"),
            ),
        )
        function_not_exist_in_inventory(
            inventories=inventories, function_name="build_product_base_model"
        )

    def test_returns_project_inventory_error(
        self, workspace_context: WorkspaceContext
    ) -> None:
        project_context = get_project_context(workspace_context, "project-b")
        root_context_result = initialize_project_context(
            project_root=workspace_context.path,
            source_root=ProjectRelativePath(Path(".")),
        )
        assert isinstance(root_context_result, Success)
        file = ProjectRelativePath(Path("test_support/invalid_helpers.py"))

        result = collect_existing_helper_inventory(
            root=root_context_result.unwrap(),
            target_project=project_context,
            files=(file,),
        )
        assert isinstance(result, Failure)
        failure = result.failure()
        assert isinstance(failure, ProjectInventoryError)

        print(format_object(failure, depth=7))
        error_contains_missing_return_type_annotation(
            failure=failure,
            file_path=file,
            project=project_context,
            workspace=workspace_context,
            function_name="create_product_summary",
        )

        error_contains_missing_parameter_type_annotation(
            failure=failure,
            file_path=file,
            project=project_context,
            workspace=workspace_context,
            function_name="create_product_base_model",
            parameter="name",
        )

        error_contains_function_reference_error(
            failure=failure,
            file_path=file,
            project=project_context,
            workspace=workspace_context,
            function_name="create_product_model",
            return_type_name="ProductModel",
        )

        error_contains_function_reference_error(
            failure=failure,
            file_path=file,
            project=project_context,
            workspace=workspace_context,
            function_name="create_product_model2",
            return_type_name="ProductModel2",
        )

    def test_returns_analysis_error(
        self,
        workspace_context: WorkspaceContext,
        mocker: MockerFixture,
    ) -> None:
        project_context = get_project_context(workspace_context, "project-b")
        root_context_result = initialize_project_context(
            project_root=workspace_context.path,
            source_root=ProjectRelativePath(Path(".")),
        )
        assert isinstance(root_context_result, Success)

        analysis_error = AnalysisError(
            message="test",
            file_path=PythonPath("gyomu_test.test"),
            phase="workspace-discovery",
        )

        load_mock = mocker.patch(
            "gyomu_test.helper.inventory.existing.load_file_analysis_context",
            return_value=Failure(analysis_error),
        )

        result = collect_existing_helper_inventory(
            root=root_context_result.unwrap(),
            target_project=project_context,
        )

        assert isinstance(result, Failure)
        assert result.failure() is analysis_error
        load_mock.assert_called_once()
