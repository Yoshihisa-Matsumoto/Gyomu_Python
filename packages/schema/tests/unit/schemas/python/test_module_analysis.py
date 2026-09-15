from gyomu_schema.schemas.python.module import ModuleAnalysis
from gyomu_schema.utility.serialization import _assert_json_round_trip

from packages.schema.schema_test_support.helpers import (
    create_function_analysis,
    create_location,
    create_module_analysis,
)


class TestModuleAnalysis:
    def test(self) -> None:
        _assert_json_round_trip(
            ModuleAnalysis,
            create_module_analysis(
                symbols=(
                    create_function_analysis(indent=0, location=create_location()),
                )
            ),
        )
