from gyomu_schema.schemas.python.function_analysis import FunctionAnalysis
from gyomu_schema.utility.serialization import _assert_json_round_trip

from packages.schema.schema_test_support.helpers import (
    create_function_analysis,
    create_location,
)


class TestFunctionAnalysis:
    def test(self) -> None:
        _assert_json_round_trip(
            FunctionAnalysis,
            create_function_analysis(indent=0, location=create_location()),
        )
