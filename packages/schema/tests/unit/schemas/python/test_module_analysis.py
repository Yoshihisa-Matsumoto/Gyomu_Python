from gyomu_schema.schemas.python.module import ModuleAnalysis
from gyomu_schema.utility.serialization import _assert_json_round_trip

from packages.schema.test_support.helpers import (
    create_function_analysis,
    create_module_analysis,
    create_source_location,
)


class TestModuleAnalysis:
    def test(self) -> None:
        _assert_json_round_trip(
            ModuleAnalysis,
            create_module_analysis(
                symbols=(
                    create_function_analysis(
                        indent=0, location=create_source_location()
                    ),
                )
            ),
        )
