from gyomu_schema.schemas.python.type.structure import (
    EllipsisStructureAnalysis,
    NameStructureAnalysis,
    NoneStructureAnalysis,
    UnknownStructureAnalysis,
)
from gyomu_schema.utility.serialization import _assert_json_round_trip


class TestNoneStructureAnalysis:
    def test(self) -> None:
        _assert_json_round_trip(
            NoneStructureAnalysis,
            NoneStructureAnalysis(),
        )


class TestNameStructureAnalysis:
    def test(self) -> None:
        _assert_json_round_trip(
            NameStructureAnalysis,
            NameStructureAnalysis(name="name1"),
        )


class TestUnknownStructureAnalysis:
    def test(self) -> None:
        _assert_json_round_trip(
            UnknownStructureAnalysis,
            UnknownStructureAnalysis(),
        )


class TestEllipsisStructureAnalysis:
    def test(self) -> None:
        _assert_json_round_trip(
            EllipsisStructureAnalysis,
            EllipsisStructureAnalysis(),
        )
