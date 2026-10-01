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
    assert issue.message == "Title is not translated"
    assert issue.repair_instruction == "Translate code block title properly"


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
    assert issue.message == "Title is created from nothing"
    assert issue.repair_instruction == (
        "Must not create sentense from non-existence title"
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
