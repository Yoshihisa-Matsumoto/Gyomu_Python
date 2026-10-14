from gyomu_schema.schemas.document.definition.common import (
    validate_text,
    validate_textblock,
)
from gyomu_schema.schemas.document.validation import ValidationIssue


class TestValidateText:
    def test_does_not_add_issue_when_literal_newline_count_matches(self) -> None:
        source = r"First paragraph.\nSecond paragraph."
        destination = r"最初の段落です。\n次の段落です。"
        issues: list[ValidationIssue] = []

        validate_text(source, destination, "text", issues)

        assert issues == []

    def test_does_not_add_issue_when_literal_newline_does_not_exist(self) -> None:
        source = "First paragraph.\nSecond paragraph."
        destination = "最初の段落です。\n次の段落です。"
        issues: list[ValidationIssue] = []

        validate_text(source, destination, "text", issues)

        assert issues == []

    def test_adds_issue_when_literal_newline_is_added(self) -> None:
        source = "First paragraph."
        destination = r"最初の段落です。\n次の段落です。"
        issues: list[ValidationIssue] = []

        validate_text(source, destination, "paragraph.text", issues)

        assert issues == [
            ValidationIssue(
                code="LITERAL_NEWLINE_MISMATCH",
                message=(
                    "The number of literal '\\n' sequences is different in paragraph.text."  # noqa: E501
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

    def test_adds_issue_when_literal_newline_is_removed(self) -> None:
        source = r"First paragraph.\nSecond paragraph."
        destination = "最初の段落です。"
        issues: list[ValidationIssue] = []

        validate_text(source, destination, "paragraph.text", issues)

        assert issues == [
            ValidationIssue(
                code="LITERAL_NEWLINE_MISMATCH",
                message=(
                    "The number of literal '\\n' sequences is different in paragraph.text."  # noqa: E501
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

    def test_adds_issue_when_literal_newline_count_differs(self) -> None:
        source = r"First.\nSecond.\nThird."
        destination = r"最初。\n次。\n最後。\n追加。"
        issues: list[ValidationIssue] = []

        validate_text(source, destination, "paragraph.text", issues)

        assert len(issues) == 1
        assert issues[0].details == {
            "source_count": "2",
            "translated_count": "3",
        }

    def test_appends_issue_to_existing_issues(self) -> None:
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
                    "The number of literal '\\n' sequences is different in paragraph.text."  # noqa: E501
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


class TestValidateTextBlock:
    def test_valid(self) -> None:
        source = ("First line.", r"Second\nline.")
        destination = ("最初の行。", r"2番目の\n行。")
        issues: list[ValidationIssue] = []

        validate_textblock(source, destination, "text", issues)

        assert issues == []

    def test_line_count_mismatch(self) -> None:
        source = ("First line.", "Second line.")
        destination = ("Translated line.",)
        issues: list[ValidationIssue] = []

        validate_textblock(source, destination, "text", issues)

        assert len(issues) == 1
        assert issues[0].code == "TEXTBLOCK_LINE_COUNT_MISMATCH"
        assert issues[0].details == {
            "source_count": "2",
            "translated_count": "1",
        }

    def test_actual_line_break_found(self) -> None:
        source = ("First line.", "Second line.")
        destination = ("First line.\nSecond line.", "Translated line.")
        issues: list[ValidationIssue] = []

        validate_textblock(source, destination, "text", issues)

        assert len(issues) == 1
        assert issues[0].code == "TEXTBLOCK_LINE_BREAK_FOUND"
        assert issues[0].details == {"line_number": "1"}
        assert "text[line 1]" in issues[0].message

    def test_literal_newline_mismatch(self) -> None:
        source = ("First\\nline.", "Second line.")
        destination = ("First line.", "Second line.")
        issues: list[ValidationIssue] = []

        validate_textblock(source, destination, "text", issues)

        assert len(issues) == 1
        assert issues[0].code == "LITERAL_NEWLINE_MISMATCH"
        assert issues[0].details == {
            "line_number": "1",
            "source_count": "1",
            "translated_count": "0",
        }
        assert "text[line 1]" in issues[0].message

    def test_multiple_issues(self) -> None:
        source = ("First\\nline.", "Second line.")
        destination = ("First line.\nSecond line.",)
        issues: list[ValidationIssue] = []

        validate_textblock(source, destination, "text", issues)

        assert [issue.code for issue in issues] == [
            "TEXTBLOCK_LINE_COUNT_MISMATCH",
            "TEXTBLOCK_LINE_BREAK_FOUND",
            "LITERAL_NEWLINE_MISMATCH",
        ]
