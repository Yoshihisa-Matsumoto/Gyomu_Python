from gyomu_schema.schemas.testing.helper import HelperConfig, HelperFileAllocation
from gyomu_schema.utility.serialization import _assert_json_round_trip

from packages.schema.test_support.testing_helpers import (
    create_helper_config,
    create_helper_file_allocation,
)


class TestHelperFileAllocation:
    def test(self) -> None:
        _assert_json_round_trip(HelperFileAllocation, create_helper_file_allocation())


class TestHelperConfig:
    def test(self) -> None:
        _assert_json_round_trip(HelperConfig, create_helper_config())
