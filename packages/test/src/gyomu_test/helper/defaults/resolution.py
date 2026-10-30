from gyomu_schema.schemas.testing.helper import HelperInventoryItem

from gyomu_test.error.parameter import (
    MissingFunctionParameterDefault,
)


def find_missing_function_parameter_defaults(
    inventory: HelperInventoryItem,
) -> tuple[MissingFunctionParameterDefault, ...] | None:
    missing_function_default_parameters: list[MissingFunctionParameterDefault] = []
    for parameter in inventory.parameters:
        if parameter.default is None:
            missing_function_default_parameters.append(
                MissingFunctionParameterDefault(
                    identity=inventory.target_identity, parameter=parameter
                )
            )

    if len(missing_function_default_parameters) > 0:
        return tuple(missing_function_default_parameters)
    return None
