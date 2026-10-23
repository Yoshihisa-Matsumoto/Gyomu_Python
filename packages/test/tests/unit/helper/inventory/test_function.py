from pathlib import Path

from gyomu_schema.schemas.python.location import SourceLocation
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.schemas.testing.helper import (
    HelperFileInventory,
)
from gyomu_test.helper.inventory.function import (
    generate_function_code,
    read_function_code,
)

from packages.schema.test_support.helpers import (
    create_helper_inventory_item,
    create_parameter_info,
    create_type_analysis,
)


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
                ),
            ),
        )

        result = generate_function_code(item)

        assert result == (
            "def create_product_summary(\n"
            "    product_id: int,\n"
            "    display_name: str,\n"
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
