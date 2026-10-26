from pathlib import Path

from gyomu_python_analysis.analysis.initialize import initialize_project_context
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_schema.schemas.python.location import SourceLocation
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.schemas.testing.helper import (
    HelperFileInventory,
)
from gyomu_test.helper.inventory.existing import collect_existing_helper_inventory
from gyomu_test.helper.inventory.function import (
    generate_function_code,
    read_function_code,
)
from gyomu_test.helper.inventory.reconcile import _normalize_python_tokens
from returns.result import Success

from packages.schema.test_support.helpers import (
    create_helper_inventory_item,
    create_literal_parameter,
    create_parameter_info,
    create_type_analysis,
)
from packages.test.tests.unit.helper.inventory.helpers import get_project_context


class TestReadFunctionCode:
    def test_extract_function_lines(self) -> None:
        source_lines = (
            "def create_product(\n",
            "    product_id: int,\n",
            ") -> Product:\n",
            "    return Product(product_id=product_id)\n",
            "\n",
            "def another_function() -> None:\n",
            "    pass\n",
        )
        file_inventory = HelperFileInventory(
            file_path=ProjectRelativePath(Path("test_support/helpers.py")),
            items=(),
            source_lines=source_lines,
        )
        location = SourceLocation(
            start_line=1,
            start_column=0,
            start_offset=0,
            end_line=4,
            end_column=0,
            end_offset=0,
        )

        result = read_function_code(file_inventory, location)

        assert result == (
            "def create_product(\n"
            "    product_id: int,\n"
            ") -> Product:\n"
            "    return Product(product_id=product_id)\n"
        )


class TestGenerateFunctionCode:
    def test_generate_function_with_parameters(self) -> None:
        item = create_helper_inventory_item(
            function_name="create_product_summary",
            parameters=(
                create_parameter_info(
                    name="product_id",
                    parameter_type=create_type_analysis("int"),
                ),
                create_parameter_info(
                    name="display_name",
                    parameter_type=create_type_analysis("str"),
                    default=create_literal_parameter(value="test name"),
                ),
            ),
        )

        result = generate_function_code(item)

        assert result == (
            "def create_product_summary(\n"
            "    product_id: int,\n"
            '    display_name: str = "test name",\n'
            ") -> ProductSummary:\n"
            "    return ProductSummary(\n"
            "        product_id=product_id,\n"
            "        display_name=display_name,\n"
            "    )\n"
        )

    def test_generate_function_without_parameters(self) -> None:
        item = create_helper_inventory_item(
            function_name="create_another_base",
        )

        result = generate_function_code(item)

        assert result == (
            "def create_another_base() -> AnotherBase:\n    return AnotherBase()\n"
        )


class TestCodeGenerationIntegration:
    def test_validate(self, workspace_context: WorkspaceContext) -> None:
        project_context = get_project_context(workspace_context, "project-b")
        root_context_result = initialize_project_context(
            project_root=workspace_context.path,
            source_root=ProjectRelativePath(Path(".")),
        )
        assert isinstance(root_context_result, Success)

        file = ProjectRelativePath(Path("test_support/helpers.py"))
        file2 = ProjectRelativePath(Path("test_support/another_helpers.py"))
        existing_result = collect_existing_helper_inventory(
            root=root_context_result.unwrap(),
            target_project=project_context,
            files=(
                file,
                file2,
            ),
        )
        assert isinstance(existing_result, Success)
        existings = existing_result.unwrap()

        for file in existings:
            print(file.file_path)
            for existing in file.items:
                print(existing.function_name)
                current_code = read_function_code(
                    file_inventory=file, location=existing.location
                )
                expected_code = generate_function_code(existing)
                assert _normalize_python_tokens(
                    current_code
                ) == _normalize_python_tokens(expected_code)

    def test_validate_parameter(self, workspace_context: WorkspaceContext) -> None:
        project_context = get_project_context(workspace_context, "parameter")
        root_context_result = initialize_project_context(
            project_root=workspace_context.path,
            source_root=ProjectRelativePath(Path(".")),
        )
        assert isinstance(root_context_result, Success)

        file = ProjectRelativePath(Path("test_support/helpers.py"))
        existing_result = collect_existing_helper_inventory(
            root=root_context_result.unwrap(),
            target_project=project_context,
            files=(file,),
        )
        assert isinstance(existing_result, Success)
        existings = existing_result.unwrap()

        for file in existings:
            print(file.file_path)
            for existing in file.items:
                print(existing.function_name)
                current_code = read_function_code(
                    file_inventory=file, location=existing.location
                )
                expected_code = generate_function_code(existing)
                assert _normalize_python_tokens(
                    current_code
                ) == _normalize_python_tokens(expected_code)
