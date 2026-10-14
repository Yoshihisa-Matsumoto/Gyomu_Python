from gyomu_schema.schemas.document.content import Paragraph, paragraph_from_text
from gyomu_schema.schemas.document.definition.paragraph import _validate_paragraph


def test_returns_valid_when_paragraph_text_is_translated() -> None:
    source = paragraph_from_text("This is a pen.")
    destination = paragraph_from_text("これはペンです。")

    result = _validate_paragraph(source, destination)

    assert result.is_valid is True
    assert result.issues == ()


def test_returns_valid_when_paragraph_text_is_unchanged() -> None:
    source = paragraph_from_text("This is a pen.")
    destination = paragraph_from_text("This is a pen.")

    result = _validate_paragraph(source, destination)

    assert result.is_valid is True
    assert result.issues == ()


def test_returns_valid_when_literal_newline_count_is_preserved() -> None:
    source = paragraph_from_text(r"First paragraph.\nSecond paragraph.")
    destination = paragraph_from_text(r"最初の段落です。\n次の段落です。")

    result = _validate_paragraph(source, destination)

    assert result.is_valid is True
    assert result.issues == ()


def test_validate_paragraph_valid() -> None:
    source = Paragraph(lines=("First line.", "Second line."))
    destination = Paragraph(lines=("最初の行。", "2番目の行。"))

    result = _validate_paragraph(source, destination)

    assert result.is_valid
    assert result.issues == ()


def test_validate_paragraph_line_count_mismatch() -> None:
    source = Paragraph(lines=("First line.", "Second line."))
    destination = Paragraph(lines=("翻訳された行。",))

    result = _validate_paragraph(source, destination)

    assert not result.is_valid
    assert len(result.issues) == 1
    assert result.issues[0].code == "TEXTBLOCK_LINE_COUNT_MISMATCH"


def test_validate_paragraph_literal_newline_mismatch() -> None:
    source = Paragraph(lines=(r"First\nline.",))
    destination = Paragraph(lines=("First line.",))

    result = _validate_paragraph(source, destination)

    assert not result.is_valid
    assert len(result.issues) == 1
    assert result.issues[0].code == "LITERAL_NEWLINE_MISMATCH"
    assert result.issues[0].details
    assert result.issues[0].details["line_number"] == "1"


def test_returns_valid_when_actual_newline_is_preserved() -> None:
    source = paragraph_from_text("First paragraph.\nSecond paragraph.")
    destination = paragraph_from_text("最初の段落です。\n次の段落です。")

    result = _validate_paragraph(source, destination)

    assert result.is_valid is True
    assert result.issues == ()
