from pathlib import Path

from gyomu_python_analysis.analysis.initialize import initialize_project_context
from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_schema.error.io import GyomuIOError, IOLayer, IOOperation
from gyomu_schema.schemas.config.test.model_defaults import (
    CallParameter,
    ListParameter,
    LiteralParameter,
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
from gyomu_test.error.test import GyomuTestError
from gyomu_test.helper.inventory.existing import collect_existing_helper_inventory
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.test.tests.unit.helper.inventory.helpers import (
    ParameterSummary,
    equal_helper_inventory,
    error_contains_duplicate,
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
        files = result.unwrap()
        assert len(files) == 1
        inventories = files[0].items
        assert files[0].file_path == ProjectRelativePath(
            Path("test_support/helpers.py")
        )
        print(inventories)
        equal_helper_inventory(
            inventories,
            symbol_id="project_b.models::ProductBaseModel",
            function_name="create_product_base_model",
            parameters=(
                ParameterSummary(
                    name="product_id",
                    parameter_type="int",
                    default=LiteralParameter(value=1),
                ),
                ParameterSummary(
                    name="name",
                    parameter_type="str",
                    default=LiteralParameter(value="Example Product"),
                ),
            ),
        )

        equal_helper_inventory(
            inventories,
            symbol_id="project_b.models::ProductSummary",
            function_name="create_product_summary",
            parameters=(
                ParameterSummary(
                    name="product_id",
                    parameter_type="int",
                    default=LiteralParameter(value=1),
                ),
                ParameterSummary(
                    name="display_name",
                    parameter_type="str",
                    default=LiteralParameter(value="Example Product"),
                ),
            ),
        )
        function_not_exist_in_inventory(
            inventories=inventories, function_name="build_product_base_model"
        )

        equal_helper_inventory(
            inventories,
            symbol_id="project_b.models::CompositeProduct",
            function_name="create_composite_product",
            parameters=(
                ParameterSummary(
                    name="composite_name",
                    parameter_type="str",
                    default=LiteralParameter(value="Test Composite"),
                ),
                ParameterSummary(
                    name="products",
                    parameter_type="tuple[ProductBaseModel, ...]",
                    default=CallParameter(
                        callable_identity=DeclarationIdentity(
                            symbol_id=SymbolId("tuple"),
                            declaration_id=DeclarationId("."),
                        ),
                        args=(
                            ListParameter(
                                elements=tuple(
                                    [
                                        CallParameter(
                                            callable_identity=DeclarationIdentity(
                                                symbol_id=SymbolId(
                                                    "packages.project_b.test_support.helpers::build_product_base_model",
                                                ),
                                                declaration_id=DeclarationId("."),
                                            )
                                        )
                                    ]
                                )
                            ),
                        ),
                    ),
                ),
            ),
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
        file2 = ProjectRelativePath(Path("test_support/another_invalid_helpers.py"))

        result = collect_existing_helper_inventory(
            root=root_context_result.unwrap(),
            target_project=project_context,
            files=(file, file2),
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
            function_name="create_product_modeler",
            return_type_name="ProductModeler",
        )

        error_contains_function_reference_error(
            failure=failure,
            file_path=file,
            project=project_context,
            workspace=workspace_context,
            function_name="create_product_model2",
            return_type_name="ProductModel2",
        )

        error_contains_duplicate(
            failure=failure,
            file_path=file,
            function_name="create_product_model",
            identity=DeclarationIdentity(
                symbol_id=SymbolId("project_b.models::ProductModel"),
                declaration_id=DeclarationId("."),
            ),
        )

        error_contains_duplicate(
            failure=failure,
            file_path=file2,
            function_name="create_product_model",
            identity=DeclarationIdentity(
                symbol_id=SymbolId("project_b.models::ProductModel"),
                declaration_id=DeclarationId("."),
            ),
        )

    def test_returns_test_error_from_analysis_error(
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
        fail = result.failure()
        assert isinstance(fail, GyomuTestError)
        assert fail.__cause__ == analysis_error
        load_mock.assert_called_once()

    def test_returns_test_error_from_gyomu_io_error(
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

        io_error = GyomuIOError(
            message="test", layer=IOLayer.FILESYSTEM, operation=IOOperation.READ
        )

        load_mock = mocker.patch(
            "gyomu_test.helper.inventory.existing.read_source_text",
            return_value=Failure(io_error),
        )

        result = collect_existing_helper_inventory(
            root=root_context_result.unwrap(),
            target_project=project_context,
        )

        assert isinstance(result, Failure)
        fail = result.failure()
        assert isinstance(fail, GyomuTestError)
        assert fail.__cause__ == io_error
        load_mock.assert_called_once()
