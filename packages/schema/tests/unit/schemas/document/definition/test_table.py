from gyomu_schema.schemas.document.definition.table import _validate_table

from packages.schema.schema_test_support.concept_helpers import (
    create_table,
    create_table_row,
)


def test_returns_valid_when_table_structure_is_unchanged() -> None:
    source = create_table(
        header=create_table_row(
            cells=("Name", "Description"),
        ),
        rows=(
            create_table_row(
                cells=("Alice", "Engineer"),
            ),
        ),
    )
    destination = create_table(
        header=create_table_row(
            cells=("Name", "Description"),
        ),
        rows=(
            create_table_row(
                cells=("Alice", "Engineer"),
            ),
        ),
    )

    result = _validate_table(source, destination)

    assert result.is_valid is True
    assert result.issues == ()


def test_returns_issue_when_header_cell_count_is_changed() -> None:
    source = create_table(
        header=create_table_row(
            cells=("Name", "Description"),
        ),
        rows=(
            create_table_row(
                cells=("Alice", "Engineer"),
            ),
        ),
    )
    destination = create_table(
        header=create_table_row(cells=("名前",)),
        rows=(
            create_table_row(
                cells=("Alice", "Engineer"),
            ),
        ),
    )

    result = _validate_table(source, destination)

    assert result.is_valid is False
    assert len(result.issues) == 1

    issue = result.issues[0]
    assert issue.code == "TABLE_HEADER_CELL_COUNT_CHANGED"
    assert issue.translation_id is None
    assert issue.details == {
        "source_count": "2",
        "translated_count": "1",
    }


def test_returns_issue_when_row_count_is_changed() -> None:
    source = create_table(
        header=create_table_row(
            cells=("Name", "Description"),
        ),
        rows=(
            create_table_row(
                cells=("Alice", "Engineer"),
            ),
            create_table_row(
                cells=("Bob", "Designer"),
            ),
        ),
    )
    destination = create_table(
        header=create_table_row(
            cells=("名前", "説明"),
        ),
        rows=(
            create_table_row(
                cells=("Alice", "Engineer"),
            ),
        ),
    )

    result = _validate_table(source, destination)

    assert result.is_valid is False
    assert len(result.issues) == 1

    issue = result.issues[0]
    assert issue.code == "TABLE_ROWS_COUNT_CHANGED"
    assert issue.translation_id is None
    assert issue.details == {
        "source_count": "2",
        "translated_count": "1",
    }


def test_returns_issue_when_row_cell_count_is_changed() -> None:
    source = create_table(
        header=create_table_row(
            cells=("Name", "Description"),
        ),
        rows=(
            create_table_row(
                cells=("Alice", "Engineer"),
            ),
        ),
    )
    destination = create_table(
        header=create_table_row(
            cells=("名前", "説明"),
        ),
        rows=(
            create_table_row(
                cells=("Alice",),
            ),
        ),
    )

    result = _validate_table(source, destination)

    assert result.is_valid is False
    assert len(result.issues) == 1

    issue = result.issues[0]
    assert issue.code == "TABLE_ROW_CELL_COUNT_CHANGED"
    assert issue.translation_id == 0
    assert issue.details == {
        "source_count": "2",
        "translated_count": "1",
    }


def test_returns_issue_when_row_cell_count_does_not_match_header() -> None:
    source = create_table(
        header=create_table_row(
            cells=("Name", "Description"),
        ),
        rows=(
            create_table_row(
                cells=("Alice",),
            ),
        ),
    )
    destination = create_table(
        header=create_table_row(
            cells=("名前", "説明"),
        ),
        rows=(
            create_table_row(
                cells=("Alice",),
            ),
        ),
    )

    result = _validate_table(source, destination)

    assert result.is_valid is False
    assert len(result.issues) == 1

    issue = result.issues[0]
    assert issue.code == "TABLE_ROW_CELL_COUNT_CHANGED"
    assert issue.translation_id == 0
    assert issue.details == {
        "source_count": "1",
        "translated_count": "1",
    }


def test_returns_issue_for_the_first_invalid_row() -> None:
    source = create_table(
        header=create_table_row(
            cells=("Name", "Description"),
        ),
        rows=(
            create_table_row(
                cells=("Alice", "Engineer"),
            ),
            create_table_row(
                cells=("Bob", "Designer"),
            ),
        ),
    )
    destination = create_table(
        header=create_table_row(
            cells=("名前", "説明"),
        ),
        rows=(
            create_table_row(
                cells=("Alice",),
            ),
            create_table_row(
                cells=("Bob",),
            ),
        ),
    )

    result = _validate_table(source, destination)

    assert result.is_valid is False
    assert len(result.issues) == 2

    assert result.issues[0].code == "TABLE_ROW_CELL_COUNT_CHANGED"
    assert result.issues[0].translation_id == 0
    assert result.issues[0].details == {
        "source_count": "2",
        "translated_count": "1",
    }

    assert result.issues[1].code == "TABLE_ROW_CELL_COUNT_CHANGED"
    assert result.issues[1].translation_id == 1
    assert result.issues[1].details == {
        "source_count": "2",
        "translated_count": "1",
    }


def test_returns_valid_when_literal_newlines_are_preserved() -> None:
    source = create_table(
        header=create_table_row(
            cells=("Name", r"Description\nDetails"),
        ),
        rows=(
            create_table_row(
                cells=("Alice", r"Engineer\nBackend"),
            ),
        ),
    )
    destination = create_table(
        header=create_table_row(
            cells=("名前", r"説明\n詳細"),
        ),
        rows=(
            create_table_row(
                cells=("アリス", r"エンジニア\nバックエンド"),
            ),
        ),
    )

    result = _validate_table(source, destination)

    assert result.is_valid is True
    assert result.issues == ()


def test_returns_issue_when_header_cell_literal_newline_is_added() -> None:
    source = create_table(
        header=create_table_row(
            cells=("Name", "Description"),
        ),
        rows=(
            create_table_row(
                cells=("Alice", "Engineer"),
            ),
        ),
    )
    destination = create_table(
        header=create_table_row(
            cells=("名前", r"説明\n詳細"),
        ),
        rows=(
            create_table_row(
                cells=("アリス", "エンジニア"),
            ),
        ),
    )

    result = _validate_table(source, destination)

    assert result.is_valid is False
    assert len(result.issues) == 1

    issue = result.issues[0]
    assert issue.code == "LITERAL_NEWLINE_MISMATCH"
    assert issue.translation_id is None
    assert issue.details == {
        "source_count": "0",
        "translated_count": "1",
    }
    assert issue.message == (
        "The number of literal '\\n' sequences is different in header->cell(1)."
    )


def test_returns_issue_when_row_cell_literal_newline_is_added() -> None:
    source = create_table(
        header=create_table_row(
            cells=("Name", "Description"),
        ),
        rows=(
            create_table_row(
                cells=("Alice", "Engineer"),
            ),
        ),
    )
    destination = create_table(
        header=create_table_row(
            cells=("名前", "説明"),
        ),
        rows=(
            create_table_row(
                cells=("アリス", r"エンジニア\nバックエンド"),
            ),
        ),
    )

    result = _validate_table(source, destination)

    assert result.is_valid is False
    assert len(result.issues) == 1

    issue = result.issues[0]
    assert issue.code == "LITERAL_NEWLINE_MISMATCH"
    assert issue.translation_id is None
    assert issue.details == {
        "source_count": "0",
        "translated_count": "1",
    }
    assert issue.message == (
        "The number of literal '\\n' sequences is different in row(0)->cell(1)."
    )


def test_returns_issue_when_row_cell_literal_newline_is_removed() -> None:
    source = create_table(
        header=create_table_row(
            cells=("Name", "Description"),
        ),
        rows=(
            create_table_row(
                cells=("Alice", r"Engineer\nBackend"),
            ),
        ),
    )
    destination = create_table(
        header=create_table_row(
            cells=("名前", "説明"),
        ),
        rows=(
            create_table_row(
                cells=("アリス", "エンジニア"),
            ),
        ),
    )

    result = _validate_table(source, destination)

    assert result.is_valid is False
    assert len(result.issues) == 1

    issue = result.issues[0]
    assert issue.code == "LITERAL_NEWLINE_MISMATCH"
    assert issue.translation_id is None
    assert issue.details == {
        "source_count": "1",
        "translated_count": "0",
    }
    assert issue.message == (
        "The number of literal '\\n' sequences is different in row(0)->cell(1)."
    )


def test_returns_all_issues_when_multiple_cells_have_literal_newline_mismatch() -> None:
    source = create_table(
        header=create_table_row(
            cells=("Name", "Description"),
        ),
        rows=(
            create_table_row(
                cells=("Alice", r"Engineer\nBackend"),
            ),
        ),
    )
    destination = create_table(
        header=create_table_row(
            cells=("名前", r"説明\n詳細"),
        ),
        rows=(
            create_table_row(
                cells=("アリス", "エンジニア"),
            ),
        ),
    )

    result = _validate_table(source, destination)

    assert result.is_valid is False
    assert len(result.issues) == 2

    assert result.issues[0].code == "LITERAL_NEWLINE_MISMATCH"
    assert result.issues[0].translation_id is None
    assert result.issues[0].details == {
        "source_count": "0",
        "translated_count": "1",
    }
    assert result.issues[0].message == (
        "The number of literal '\\n' sequences is different in header->cell(1)."
    )

    assert result.issues[1].code == "LITERAL_NEWLINE_MISMATCH"
    assert result.issues[1].translation_id is None
    assert result.issues[1].details == {
        "source_count": "1",
        "translated_count": "0",
    }
    assert result.issues[1].message == (
        "The number of literal '\\n' sequences is different in row(0)->cell(1)."
    )
