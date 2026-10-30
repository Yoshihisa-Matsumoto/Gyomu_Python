from unittest.mock import MagicMock

from gyomu_schema.schemas.python.types import DeclarationIdentity
from gyomu_schema.schemas.testing.helper import (
    HelperInventoryItem,
    ParameterInfo,
)
from gyomu_test.error.parameter import MissingFunctionParameterDefault
from gyomu_test.helper.defaults.resolution import (
    find_missing_function_parameter_defaults,
)


class TestFindMissingFunctionParameterDefaults:
    def test_returns_none_when_all_parameters_have_defaults(self) -> None:
        parameter_with_default = ParameterInfo(
            name="name",
            parameter_type=MagicMock(),
            default=MagicMock(),
        )
        inventory = HelperInventoryItem(
            target_identity=MagicMock(spec=DeclarationIdentity),
            function_name="create_example",
            parameters=(parameter_with_default,),
        )

        actual = find_missing_function_parameter_defaults(inventory)

        assert actual is None

    def test_returns_missing_parameter_when_default_is_none(self) -> None:
        identity = MagicMock(spec=DeclarationIdentity)
        parameter_without_default = ParameterInfo(
            name="name",
            parameter_type=MagicMock(),
            default=None,
        )
        inventory = HelperInventoryItem(
            target_identity=identity,
            function_name="create_example",
            parameters=(parameter_without_default,),
        )

        actual = find_missing_function_parameter_defaults(inventory)

        assert actual == (
            MissingFunctionParameterDefault(
                identity=identity,
                parameter=parameter_without_default,
            ),
        )

    def test_returns_all_parameters_without_defaults(self) -> None:
        identity = MagicMock(spec=DeclarationIdentity)
        parameter_with_default = ParameterInfo(
            name="name",
            parameter_type=MagicMock(),
            default=MagicMock(),
        )
        first_parameter_without_default = ParameterInfo(
            name="package",
            parameter_type=MagicMock(),
            default=None,
        )
        second_parameter_without_default = ParameterInfo(
            name="completed_steps",
            parameter_type=MagicMock(),
            default=None,
        )
        inventory = HelperInventoryItem(
            target_identity=identity,
            function_name="create_example",
            parameters=(
                parameter_with_default,
                first_parameter_without_default,
                second_parameter_without_default,
            ),
        )

        actual = find_missing_function_parameter_defaults(inventory)

        assert actual == (
            MissingFunctionParameterDefault(
                identity=identity,
                parameter=first_parameter_without_default,
            ),
            MissingFunctionParameterDefault(
                identity=identity,
                parameter=second_parameter_without_default,
            ),
        )

    def test_returns_none_when_inventory_has_no_parameters(self) -> None:
        inventory = HelperInventoryItem(
            target_identity=MagicMock(spec=DeclarationIdentity),
            function_name="create_example",
            parameters=(),
        )

        actual = find_missing_function_parameter_defaults(inventory)

        assert actual is None
