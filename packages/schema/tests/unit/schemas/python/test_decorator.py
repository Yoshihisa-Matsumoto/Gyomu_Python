from gyomu_schema.schemas.python.decorator import DecoratorAnalysis, DecoratorArgument
from gyomu_schema.utility.serialization import _assert_json_round_trip

from packages.schema.schema_test_support.helpers import (
    create_literal_value,
    create_location,
)


class TestDecoratorAnalysis:
    def test(self) -> None:
        _assert_json_round_trip(
            DecoratorAnalysis,
            DecoratorAnalysis(
                name="dec1",
                arguments=(
                    DecoratorArgument(
                        name="arg1", expression=create_literal_value("val1")
                    ),
                ),
                location=create_location(),
            ),
        )
