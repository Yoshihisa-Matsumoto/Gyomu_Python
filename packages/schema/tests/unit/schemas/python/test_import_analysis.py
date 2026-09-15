from gyomu_schema.schemas.python.import_analysis import ImportAnalysis, ImportKind
from gyomu_schema.utility.serialization import _assert_json_round_trip


class TestImportAnalysis:
    def test(self) -> None:
        _assert_json_round_trip(
            ImportAnalysis,
            ImportAnalysis(
                local_name="loc1", imported_name="ABC", kind=ImportKind.SYMBOL
            ),
        )
