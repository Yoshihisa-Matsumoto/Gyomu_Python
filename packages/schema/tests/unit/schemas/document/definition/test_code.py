from gyomu_schema.schemas.document.definition.code import _validate_codeblock

from packages.schema.schema_test_support.concept_helpers import create_codeblock


def test_returns_valid_when_codeblock_is_unchanged() -> None:
    source = create_codeblock(
        language="python",
        code="print('hello')",
        title="Example",
    )
    destination = create_codeblock(
        language="python",
        code="print('hello')",
        title="例",
    )

    result = _validate_codeblock(source, destination)

    assert result.is_valid
    assert result.issues == ()


def test_returns_issue_when_source_title_is_missing_in_destination() -> None:
    source = create_codeblock(
        language="python",
        code="print('hello')",
        title="Example",
    )
    destination = create_codeblock(
        language="python",
        code="print('hello')",
    )

    result = _validate_codeblock(source, destination)

    assert not result.is_valid
    assert len(result.issues) == 1

    issue = result.issues[0]
    assert issue.code == "CODE_BLOCK_TITLE_MISMATCH"
    assert issue.message == "Code block title is missing from the translation."
    assert issue.repair_instruction == (
        "Translate the code block title when the source has one."
    )


def test_returns_issue_when_destination_creates_title() -> None:
    source = create_codeblock(
        language="python",
        code="print('hello')",
    )
    destination = create_codeblock(
        language="python",
        code="print('hello')",
        title="Example",
    )

    result = _validate_codeblock(source, destination)

    assert not result.is_valid
    assert len(result.issues) == 1

    issue = result.issues[0]
    assert issue.code == "CODE_BLOCK_TITLE_MISMATCH"
    assert issue.message == (
        "Code block title was created although the source has no title."
    )
    assert issue.repair_instruction == (
        "Must not create a title from when the source has no title."
    )


def test_returns_issue_when_codeblock_title_contains_line_break() -> None:
    source = create_codeblock(
        language="python",
        code="print('hello')",
        title="Example",
    )
    destination = create_codeblock(
        language="python",
        code="print('hello')",
        title="例\n題",
    )

    result = _validate_codeblock(source, destination)

    assert not result.is_valid
    assert len(result.issues) == 1

    issue = result.issues[0]
    assert issue.code == "CODE_BLOCK_TITLE_MULTILINE"
    assert issue.message == "Code block title must be a single line."
    assert issue.details == {
        "line_break_count": "1",
    }
    assert issue.repair_instruction == (
        "- Keep the code block title on a single line.\n"
        "- Remove all line breaks from the code block title."
    )


def test_returns_issue_when_code_is_changed() -> None:
    source = create_codeblock(
        language="python",
        code="print('hello')",
        title="Example",
    )
    destination = create_codeblock(
        language="python",
        code="print('こんにちは')",
        title="例",
    )

    result = _validate_codeblock(source, destination)

    assert not result.is_valid
    assert len(result.issues) == 1

    issue = result.issues[0]
    assert issue.code == "CODE_BLOCK_CODE_MISMATCH"
    assert issue.message == "code is translated"
    assert issue.repair_instruction == ("code MUST not be translated or transformed")


def test_returns_issue_when_language_is_changed() -> None:
    source = create_codeblock(
        language="python",
        code="print('hello')",
        title="Example",
    )
    destination = create_codeblock(
        language="javascript",
        code="print('hello')",
        title="例",
    )

    result = _validate_codeblock(source, destination)

    assert not result.is_valid
    assert len(result.issues) == 1

    issue = result.issues[0]
    assert issue.code == "CODE_BLOCK_LANGUAGE_MISMATCH"
    assert issue.message == "language is translated"
    assert issue.repair_instruction == (
        "language MUST not be translated or transformed"
    )


def test_returns_all_issues_when_multiple_fields_are_changed() -> None:
    source = create_codeblock(
        language="python",
        code="print('hello')",
        title="Example",
    )
    destination = create_codeblock(
        language="javascript",
        code="print('こんにちは')",
        title=None,
    )

    result = _validate_codeblock(source, destination)

    assert not result.is_valid
    assert len(result.issues) == 3

    assert [issue.code for issue in result.issues] == [
        "CODE_BLOCK_TITLE_MISMATCH",
        "CODE_BLOCK_CODE_MISMATCH",
        "CODE_BLOCK_LANGUAGE_MISMATCH",
    ]
