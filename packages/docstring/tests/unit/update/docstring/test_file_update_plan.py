from gyomu_docstring.update.docstring.file_update_plan import (
    FileUpdatePlan,
    FileUpdatePlanEntry,
)
from gyomu_schema.utility.serialization import _assert_json_round_trip

from packages.schema.schema_test_support.helpers import (
    create_declaration_identity,
    create_location,
)


class TestFileUpdatePlanEntry:
    def test(self) -> None:
        _assert_json_round_trip(
            FileUpdatePlanEntry,
            FileUpdatePlanEntry(
                identity=create_declaration_identity(id="TestID"),
                location=create_location(start_line=1),
                new_text="ABCDEF###",
            ),
        )


class TestFileUpdatePlan:
    def test(self) -> None:
        _assert_json_round_trip(
            FileUpdatePlan,
            FileUpdatePlan(
                items=(
                    FileUpdatePlanEntry(
                        identity=create_declaration_identity(id="TestID"),
                        location=create_location(start_line=1),
                        new_text="ABCDEF###",
                    ),
                    FileUpdatePlanEntry(
                        identity=create_declaration_identity(id="TestID2"),
                        location=create_location(start_line=3),
                        new_text="ABCDEFEFE###",
                    ),
                )
            ),
        )
