from gyomu_schema.schemas.knowledge.technical import Technical
from gyomu_schema.utility.serialization import _assert_json_round_trip

from packages.schema.schema_test_support.concept_helpers import create_technical


class TestTechnical:
    def test(self) -> None:
        _assert_json_round_trip(Technical, create_technical())
