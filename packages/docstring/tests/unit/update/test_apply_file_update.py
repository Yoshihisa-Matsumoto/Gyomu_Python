from gyomu_docstring.update.apply_file_update import apply_file_update_plan
from gyomu_docstring.update.docstring.file_update_plan import (
    FileUpdatePlan,
)

from packages.docstring.docstring_test_support.helpers import create_entry
from packages.schema.schema_test_support.helpers import (
    create_declaration_identity,
)


class TestApplyFileUpdate:
    def test_applies_replacement(self) -> None:
        source = "abcdefghij"

        plan = FileUpdatePlan(
            items=(
                create_entry(
                    identity=create_declaration_identity("replace"),
                    start_offset=2,
                    end_offset=5,
                    new_text="XYZ",
                ),
            )
        )

        result = apply_file_update_plan(source, plan)

        assert result == "abXYZfghij"

    def test_applies_addition(self) -> None:
        source = "abcdefghij"

        plan = FileUpdatePlan(
            items=(
                create_entry(
                    identity=create_declaration_identity("add"),
                    start_offset=5,
                    end_offset=5,
                    new_text="XYZ",
                ),
            )
        )

        result = apply_file_update_plan(source, plan)

        assert result == "abcdeXYZfghij"

    def test_applies_deletion(self) -> None:
        source = "abcdefghij"

        plan = FileUpdatePlan(
            items=(
                create_entry(
                    identity=create_declaration_identity("delete"),
                    start_offset=2,
                    end_offset=5,
                    new_text="",
                ),
            )
        )

        result = apply_file_update_plan(source, plan)

        assert result == "abfghij"

    def test_applies_multiple_updates(self) -> None:
        source = "abcdefghij"

        plan = FileUpdatePlan(
            items=(
                create_entry(
                    identity=create_declaration_identity("XX"),
                    start_offset=2,
                    end_offset=4,
                    new_text="XX",
                ),
                create_entry(
                    identity=create_declaration_identity("YYY"),
                    start_offset=6,
                    end_offset=6,
                    new_text="YYY",
                ),
                create_entry(
                    identity=create_declaration_identity("Z"),
                    start_offset=8,
                    end_offset=10,
                    new_text="",
                ),
            )
        )

        result = apply_file_update_plan(source, plan)

        assert result == "abXXefYYYgh"

    def test_applies_empty_plan(self) -> None:
        source = "abcdefghij"

        plan = FileUpdatePlan(items=())

        result = apply_file_update_plan(source, plan)

        assert result == source
