from gyomu_schema.schemas.python.variable import VariableAnalysis
from gyomu_schema.utility.serialization import _assert_json_round_trip

from packages.schema.schema_test_support.helpers import (
    create_declaration_identity,
    create_literal_value,
    create_location,
    create_pydantic_field_analysis,
    create_variable_analysis,
)


class TestVariableAnalysis:
    def test(self) -> None:
        _assert_json_round_trip(
            VariableAnalysis,
            create_variable_analysis(
                indent=0,
                location=create_location(),
                name="var1",
                identity=create_declaration_identity("var1"),
                value_source="int",
                pydantic=create_pydantic_field_analysis(
                    required=False,
                    default_source="None",
                    description="This is test",
                    alias="Alias",
                ),
                value_expression=create_literal_value(1),
            ),
        )
