from gyomu_schema.schemas.knowledge.package import (
    Package,
)
from gyomu_schema.utility.serialization import _assert_json_round_trip

from packages.schema.schema_test_support.concept_helpers import create_package


class TestPackage:
    def test(self) -> None:
        _assert_json_round_trip(Package, create_package())
