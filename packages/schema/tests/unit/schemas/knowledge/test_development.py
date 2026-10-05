from gyomu_schema.schemas.knowledge.development import (
    Development,
)
from gyomu_schema.utility.serialization import _assert_json_round_trip

from packages.schema.schema_test_support.concept_helpers import create_development


class TestDevelopment:
    def test(self) -> None:
        _assert_json_round_trip(Development, create_development())
