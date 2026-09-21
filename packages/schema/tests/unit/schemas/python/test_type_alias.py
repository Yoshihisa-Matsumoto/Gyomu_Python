from gyomu_schema.schemas.python.type_alias import TypeAliasAnalysis
from gyomu_schema.utility.serialization import _assert_json_round_trip

from packages.schema.schema_test_support.helpers import (
    create_location,
    create_type_alias_analysis,
)


class TestTypeAliasAnalysis:
    def test(self) -> None:
        _assert_json_round_trip(
            TypeAliasAnalysis,
            create_type_alias_analysis(indent=0, location=create_location()),
        )
