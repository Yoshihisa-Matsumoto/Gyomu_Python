from gyomu_schema.schemas.python.location import SourceLocation
from gyomu_schema.schemas.testing.helper import HelperFileInventory, HelperInventoryItem

from gyomu_test.helper.inventory.naming import _build_class_name_from_helper_name


def read_function_code(
    file_inventory: HelperFileInventory,
    location: SourceLocation,
) -> str:
    return "".join(
        file_inventory.source_lines[location.start_line - 1 : location.end_line]
    )


def generate_function_code(item: HelperInventoryItem) -> str:
    return_type = _build_class_name_from_helper_name(function_name=item.function_name)

    if not item.parameters:
        return (
            f"def {item.function_name}() -> {return_type}:\n"
            f"    return {return_type}()\n"
        )

    parameters = ",\n".join(
        f"    {parameter.name}: {parameter.parameter_type.text}"
        for parameter in item.parameters
    )
    arguments = ",\n".join(
        f"        {parameter.name}={parameter.name}" for parameter in item.parameters
    )

    return (
        f"def {item.function_name}(\n"
        f"{parameters},\n"
        f") -> {return_type}:\n"
        f"    return {return_type}(\n"
        f"{arguments},\n"
        f"    )\n"
    )
