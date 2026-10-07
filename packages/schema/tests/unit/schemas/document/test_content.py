from gyomu_schema.schemas.document.content import (
    BulletList,
    CodeBlock,
    Paragraph,
    Table,
)
from gyomu_schema.utility.serialization import _assert_json_round_trip

from packages.schema.schema_test_support.concept_helpers import (
    create_bullet_list,
    create_bullet_list_item,
    create_codeblock,
    create_paragraph,
    create_table,
    create_table_row,
)


class TestParagraph:
    def test(self) -> None:
        _assert_json_round_trip(
            Paragraph,
            create_paragraph(
                text="This is a test paragraph.",
            ),
        )


class TestCodeBlock:
    def test(self) -> None:
        _assert_json_round_trip(
            CodeBlock,
            create_codeblock(code="This is a test code block.", title="Python"),
        )


class TestTable:
    def test(self) -> None:
        _assert_json_round_trip(
            Table,
            create_table(
                header=create_table_row(cells=("Header 1", "Header 2")),
                rows=(
                    create_table_row(cells=("Cell 1", "Cell 2")),
                    create_table_row(cells=("Cell 3", "Cell 4")),
                ),
            ),
        )


class TestBulletList:
    def test(self) -> None:
        _assert_json_round_trip(
            BulletList,
            create_bullet_list(
                items=(
                    create_bullet_list_item(text="Item 1"),
                    create_bullet_list_item(text="Item 2"),
                ),
            ),
        )
