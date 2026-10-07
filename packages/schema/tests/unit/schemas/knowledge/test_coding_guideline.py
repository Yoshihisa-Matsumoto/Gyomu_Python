from gyomu_schema.schemas.knowledge.coding_guideline import CodingGuideline
from gyomu_schema.utility.serialization import _assert_json_round_trip

from packages.schema.schema_test_support.concept_helpers import create_coding_guideline


class TestCodingGuideline:
    def test(self) -> None:
        _assert_json_round_trip(CodingGuideline, create_coding_guideline())
