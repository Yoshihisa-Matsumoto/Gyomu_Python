from gyomu_schema.schemas.knowledge.roadmap import Roadmap
from gyomu_schema.utility.serialization import _assert_json_round_trip

from packages.schema.schema_test_support.concept_helpers import create_roadmap


class TestRoadmap:
    def test(self) -> None:
        _assert_json_round_trip(Roadmap, create_roadmap())
