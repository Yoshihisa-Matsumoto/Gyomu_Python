from gyomu_schema.schemas.document.definition.common import validate_text
from gyomu_schema.schemas.document.validation import ValidationIssue


def test_validate_text_does_not_add_issue_when_literal_newline_count_matches() -> None:
    source = r"First paragraph.\nSecond paragraph."
    destination = r"最初の段落です。\n次の段落です。"
    issues: list[ValidationIssue] = []

    validate_text(source, destination, "text", issues)

    assert issues == []


def test_validate_text_does_not_add_issue_when_literal_newline_does_not_exist() -> None:
    source = "First paragraph.\nSecond paragraph."
    destination = "最初の段落です。\n次の段落です。"
    issues: list[ValidationIssue] = []

    validate_text(source, destination, "text", issues)

    assert issues == []


def test_validate_text_adds_issue_when_literal_newline_is_added() -> None:
    source = "First paragraph."
    destination = r"最初の段落です。\n次の段落です。"
    issues: list[ValidationIssue] = []

    validate_text(source, destination, "paragraph.text", issues)

    assert issues == [
        ValidationIssue(
            code="LITERAL_NEWLINE_MISMATCH",
            message=(
                "The number of literal '\\n' sequences is different in paragraph.text."
            ),
            details={
                "source_count": "0",
                "translated_count": "1",
            },
            repair_instruction=(
                "- Preserve the same number of literal `\\n` sequences "
                "as in the source.\n"
                "- Do not add, remove, or replace literal `\\n` sequences."
            ),
        )
    ]


def test_validate_text_adds_issue_when_literal_newline_is_removed() -> None:
    source = r"First paragraph.\nSecond paragraph."
    destination = "最初の段落です。"
    issues: list[ValidationIssue] = []

    validate_text(source, destination, "paragraph.text", issues)

    assert issues == [
        ValidationIssue(
            code="LITERAL_NEWLINE_MISMATCH",
            message=(
                "The number of literal '\\n' sequences is different in paragraph.text."
            ),
            details={
                "source_count": "1",
                "translated_count": "0",
            },
            repair_instruction=(
                "- Preserve the same number of literal `\\n` sequences "
                "as in the source.\n"
                "- Do not add, remove, or replace literal `\\n` sequences."
            ),
        )
    ]


def test_validate_text_adds_issue_when_literal_newline_count_differs() -> None:
    source = r"First.\nSecond.\nThird."
    destination = r"最初。\n次。\n最後。\n追加。"
    issues: list[ValidationIssue] = []

    validate_text(source, destination, "paragraph.text", issues)

    assert len(issues) == 1
    assert issues[0].details == {
        "source_count": "2",
        "translated_count": "3",
    }


def test_validate_text_appends_issue_to_existing_issues() -> None:
    source = "First paragraph."
    destination = r"最初の段落です。\n"
    existing_issue = ValidationIssue(
        code="EXISTING_ERROR",
        message="Existing error",
        details={},
        repair_instruction="Fix the existing error.",
    )
    issues = [existing_issue]

    validate_text(source, destination, "paragraph.text", issues)

    assert issues == [
        existing_issue,
        ValidationIssue(
            code="LITERAL_NEWLINE_MISMATCH",
            message=(
                "The number of literal '\\n' sequences is different in paragraph.text."
            ),
            details={
                "source_count": "0",
                "translated_count": "1",
            },
            repair_instruction=(
                "- Preserve the same number of literal `\\n` sequences "
                "as in the source.\n"
                "- Do not add, remove, or replace literal `\\n` sequences."
            ),
        ),
    ]
