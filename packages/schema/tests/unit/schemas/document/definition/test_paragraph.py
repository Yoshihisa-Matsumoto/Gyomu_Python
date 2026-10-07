from gyomu_schema.schemas.document.definition.paragraph import _validate_paragraph
from gyomu_schema.schemas.document.validation import ValidationIssue

from packages.schema.schema_test_support.concept_helpers import create_paragraph


def test_returns_valid_when_paragraph_text_is_translated() -> None:
    source = create_paragraph("This is a pen.")
    destination = create_paragraph("これはペンです。")

    result = _validate_paragraph(source, destination)

    assert result.is_valid is True
    assert result.issues == ()


def test_returns_valid_when_paragraph_text_is_unchanged() -> None:
    source = create_paragraph("This is a pen.")
    destination = create_paragraph("This is a pen.")

    result = _validate_paragraph(source, destination)

    assert result.is_valid is True
    assert result.issues == ()


def test_returns_valid_when_literal_newline_count_is_preserved() -> None:
    source = create_paragraph(r"First paragraph.\nSecond paragraph.")
    destination = create_paragraph(r"最初の段落です。\n次の段落です。")

    result = _validate_paragraph(source, destination)

    assert result.is_valid is True
    assert result.issues == ()


def test_returns_invalid_when_literal_newline_is_added() -> None:
    source = create_paragraph("First paragraph.")
    destination = create_paragraph(r"最初の段落です。\n次の段落です。")

    result = _validate_paragraph(source, destination)

    assert result.is_valid is False
    assert result.issues == (
        ValidationIssue(
            code="LITERAL_NEWLINE_MISMATCH",
            message="The number of literal '\\n' sequences is different in text.",
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
    )


def test_returns_valid_when_actual_newline_is_preserved() -> None:
    source = create_paragraph("First paragraph.\nSecond paragraph.")
    destination = create_paragraph("最初の段落です。\n次の段落です。")

    result = _validate_paragraph(source, destination)

    assert result.is_valid is True
    assert result.issues == ()
