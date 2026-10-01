from gyomu_schema.schemas.document.definition.paragraph import _validate_paragraph

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
