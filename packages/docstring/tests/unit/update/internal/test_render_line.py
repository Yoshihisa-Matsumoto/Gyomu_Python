import pytest
from gyomu_docstring.update.docstring.line import (
    DocstringBlank,
    DocstringLine,
    DocstringSectionItem,
    DocstringText,
)
from gyomu_docstring.update.docstring.updated_docstring import UpdatedDocstring
from gyomu_docstring.update.internal.render_line import (
    render_docstring_lines,
    wrap_docstring_item,
    wrap_docstring_summary,
    wrap_text,
)
from gyomu_schema.schemas.python.docstring import (
    DocstringAnalysis,
    DocstringCustomListSection,
    DocstringCustomNamedSectionItem,
    DocstringCustomSection,
    DocstringGyomuContextSection,
    DocstringNotesSection,
    DocstringParametersSection,
    DocstringParametersSectionItem,
    DocstringRaisesSection,
    DocstringRaisesSectionItem,
    DocstringReturnsSection,
    DocstringReturnsSectionItem,
    DocstringSection,
    DocstringStyle,
)

from packages.schema.schema_test_support.helpers import (
    _default_identity,
    create_location,
)


def create_updated_docstring(
    summary: str | None,
    description: str | None = None,
    sections: tuple[DocstringSection, ...] | None = None,
    indent: int = 4,
) -> UpdatedDocstring:
    return UpdatedDocstring(
        identity=_default_identity,
        docstring=DocstringAnalysis(
            summary=summary,
            description=description,
            style=DocstringStyle.GOOGLE,
            location=create_location(0, 0),
            sections=sections if sections is not None else tuple(),
            raw="",
            indent=indent,
        ),
    )


def test_renders_summary() -> None:
    updated = create_updated_docstring(
        summary="Finds a user.",
    )

    result = render_docstring_lines(updated, 88)

    assert result == (DocstringText(text="Finds a user."),)


def test_renders_summary_and_description() -> None:
    updated = create_updated_docstring(
        summary="Finds a user.",
        description="Searches the repository.",
    )

    result = render_docstring_lines(updated, 88)

    assert result == (
        DocstringText(text="Finds a user."),
        DocstringBlank(),
        DocstringText(text="Searches the repository."),
    )


def test_renders_blank_when_summary_is_none() -> None:
    updated = create_updated_docstring(
        summary=None,
        sections=(
            DocstringParametersSection(
                items=(
                    DocstringParametersSectionItem(
                        name="user_id",
                        type="int",
                        description="User identifier.",
                    ),
                ),
            ),
        ),
    )

    result = render_docstring_lines(updated, 88)

    assert result == (
        DocstringBlank(),
        DocstringSectionItem(text="Args:"),
        DocstringText(text="    user_id (int): User identifier."),
    )


def test_renders_parameters() -> None:
    updated = create_updated_docstring(
        summary="Finds a user.",
        sections=(
            DocstringParametersSection(
                items=(
                    DocstringParametersSectionItem(
                        name="user_id",
                        type="int",
                        description="User identifier.",
                    ),
                    DocstringParametersSectionItem(
                        name="name",
                        type=None,
                        description="User name.",
                    ),
                ),
            ),
        ),
    )

    result = render_docstring_lines(updated, 88)

    assert result == (
        DocstringText(text="Finds a user."),
        DocstringBlank(),
        DocstringSectionItem(text="Args:"),
        DocstringText(text="    user_id (int): User identifier."),
        DocstringText(text="    name: User name."),
    )


def test_renders_returns() -> None:
    updated = create_updated_docstring(
        summary="Finds a user.",
        sections=(
            DocstringReturnsSection(
                item=DocstringReturnsSectionItem(
                    type="User",
                    description="The matching user.",
                ),
            ),
        ),
    )

    result = render_docstring_lines(updated, 88)

    assert result == (
        DocstringText(text="Finds a user."),
        DocstringBlank(),
        DocstringSectionItem(text="Returns:"),
        DocstringText(text="    User: The matching user."),
    )


def test_renders_returns_without_type() -> None:
    updated = create_updated_docstring(
        summary="Finds a user.",
        sections=(
            DocstringReturnsSection(
                item=DocstringReturnsSectionItem(
                    type=None,
                    description="The matching user.",
                ),
            ),
        ),
    )

    result = render_docstring_lines(updated, 88)

    assert result == (
        DocstringText(text="Finds a user."),
        DocstringBlank(),
        DocstringSectionItem(text="Returns:"),
        DocstringText(text="    The matching user."),
    )


def test_renders_raises() -> None:
    updated = create_updated_docstring(
        summary="Finds a user.",
        sections=(
            DocstringRaisesSection(
                items=(
                    DocstringRaisesSectionItem(
                        type="ValueError",
                        description="If the user does not exist.",
                    ),
                ),
            ),
        ),
    )

    result = render_docstring_lines(updated, 88)

    assert result == (
        DocstringText(text="Finds a user."),
        DocstringBlank(),
        DocstringSectionItem(text="Raises:"),
        DocstringText(
            text="    ValueError: If the user does not exist.",
        ),
    )


# def test_renders_raises_without_type() -> None:
#     updated = create_updated_docstring(
#         summary="Finds a user.",
#         sections=(
#             DocstringRaisesSection(
#                 items=(
#                     DocstringRaisesSectionItem(
#                         type=None,
#                         description="If the user does not exist.",
#                     ),
#                 ),
#             ),
#         ),
#     )

#     result = render_docstring_lines(updated,88)

#     assert result == (
#         DocstringText("Finds a user."),
#         DocstringBlank(),
#         DocstringSectionItem("Raises:"),
#         DocstringText(
#             "    If the user does not exist.",
#         ),
#     )


def test_renders_multiple_raises() -> None:
    updated = create_updated_docstring(
        summary="Finds a user.",
        sections=(
            DocstringRaisesSection(
                items=(
                    DocstringRaisesSectionItem(
                        type="ValueError",
                        description="If the user does not exist.",
                    ),
                    DocstringRaisesSectionItem(
                        type="PermissionError",
                        description="If access is denied.",
                    ),
                ),
            ),
        ),
    )

    result = render_docstring_lines(updated, 88)

    assert result == (
        DocstringText(text="Finds a user."),
        DocstringBlank(),
        DocstringSectionItem(text="Raises:"),
        DocstringText(
            text="    ValueError: If the user does not exist.",
        ),
        DocstringText(
            text="    PermissionError: If access is denied.",
        ),
    )


def test_renders_all_standard_sections() -> None:
    updated = create_updated_docstring(
        summary="Finds a user.",
        description="Searches the repository.",
        sections=(
            DocstringParametersSection(
                items=(
                    DocstringParametersSectionItem(
                        name="user_id",
                        type="int",
                        description="User identifier.",
                    ),
                    DocstringParametersSectionItem(
                        name="name",
                        type=None,
                        description="User name.",
                    ),
                ),
            ),
            DocstringReturnsSection(
                item=DocstringReturnsSectionItem(
                    type="User",
                    description="The matching user.",
                ),
            ),
            DocstringRaisesSection(
                items=(
                    DocstringRaisesSectionItem(
                        type="ValueError",
                        description="If the user does not exist.",
                    ),
                ),
            ),
        ),
    )

    result = render_docstring_lines(updated, 88)

    assert result == (
        DocstringText(text="Finds a user."),
        DocstringBlank(),
        DocstringText(text="Searches the repository."),
        DocstringBlank(),
        DocstringSectionItem(text="Args:"),
        DocstringText(text="    user_id (int): User identifier."),
        DocstringText(text="    name: User name."),
        DocstringBlank(),
        DocstringSectionItem(text="Returns:"),
        DocstringText(text="    User: The matching user."),
        DocstringBlank(),
        DocstringSectionItem(text="Raises:"),
        DocstringText(
            text="    ValueError: If the user does not exist.",
        ),
    )


def test_renders_notes() -> None:
    updated = create_updated_docstring(
        summary="Finds a user.",
        sections=(
            DocstringNotesSection(
                value="This operation uses the repository cache.",
            ),
        ),
    )

    result = render_docstring_lines(updated, 88)

    assert result == (
        DocstringText(text="Finds a user."),
        DocstringBlank(),
        DocstringSectionItem(text="Notes:"),
        DocstringText(
            text="    This operation uses the repository cache.",
        ),
    )


def test_renders_gyomu_context() -> None:
    updated = create_updated_docstring(
        summary="Finds a user.",
        sections=(
            DocstringGyomuContextSection(
                value="Used by the user lookup workflow.",
            ),
        ),
    )

    result = render_docstring_lines(updated, 88)

    assert result == (
        DocstringText(text="Finds a user."),
        DocstringBlank(),
        DocstringSectionItem(text="Gyomu Context:"),
        DocstringText(
            text="    Used by the user lookup workflow.",
        ),
    )


def test_renders_custom_section() -> None:
    updated = create_updated_docstring(
        summary="Finds a user.",
        sections=(
            DocstringCustomSection(
                title="Warning",
                value="This operation may be expensive.",
            ),
        ),
    )

    result = render_docstring_lines(updated, 88)

    assert result == (
        DocstringText(text="Finds a user."),
        DocstringBlank(),
        DocstringSectionItem(text="Warning:"),
        DocstringText(
            text="    This operation may be expensive.",
        ),
    )


def test_renders_custom_list_section() -> None:
    updated = create_updated_docstring(
        summary="Finds a user.",
        sections=(
            DocstringCustomListSection(
                title="Attributes",
                items=(
                    DocstringCustomNamedSectionItem(
                        name="user_id",
                        value="The user ID.",
                    ),
                    DocstringCustomNamedSectionItem(
                        name="name",
                        value="The user name.",
                    ),
                ),
            ),
        ),
    )

    result = render_docstring_lines(updated, 88)

    assert result == (
        DocstringText(text="Finds a user."),
        DocstringBlank(),
        DocstringSectionItem(text="Attributes:"),
        DocstringText(
            text="    user_id: The user ID.",
        ),
        DocstringText(
            text="    name: The user name.",
        ),
    )


@pytest.mark.parametrize(
    ("text", "max_length", "expected"),
    [
        (
            "This is a simple sentence.",
            100,
            ("This is a simple sentence.",),
        ),
        (
            "This is a simple sentence.",
            10,
            ("This is a", "simple", "sentence."),
        ),
        (
            "This is a very long description.",
            15,
            ("This is a very", "long", "description."),
        ),
        (
            "This-is-a-very-long-word",
            10,
            ("This-is-a-very-long-word",),
        ),
        (
            "",
            20,
            (),
        ),
        (
            "first line\nsecond line",
            100,
            ("first line", "second line"),
        ),
        (
            "first line\n\nsecond line",
            100,
            ("first line", "", "second line"),
        ),
        (
            "This is a long line.\nThis is another long line.",
            10,
            (
                "This is a",
                "long line.",
                "This is",
                "another",
                "long line.",
            ),
        ),
    ],
)
def test_wrap_text(
    text: str,
    max_length: int,
    expected: tuple[str, ...],
) -> None:
    assert wrap_text(text, max_length) == expected


@pytest.mark.parametrize(
    ("text", "max_length", "expected"),
    [
        (
            "12345 67890",
            11,
            ("12345 67890",),
        ),
        (
            "12345 67890",
            10,
            ("12345", "67890"),
        ),
        (
            "This is a very long description.",
            15,
            ("This is a very", "long", "description."),
        ),
        (
            "This-is-a-very-long-word",
            10,
            ("This-is-a-very-long-word",),
        ),
    ],
)
def test_wrap_text_boundary_cases(
    text: str,
    max_length: int,
    expected: tuple[str, ...],
) -> None:
    assert wrap_text(text, max_length) == expected


@pytest.mark.parametrize(
    ("text", "line_length", "expected"),
    [
        # 1. そのまま1行
        (
            "12345 67890",
            20,
            ("    12345 67890",),
        ),
        # 2. ちょうど境界
        (
            "123456789 123456",
            20,
            ("    123456789 123456",),
        ),
        # 3. 1行目の幅を超えて折り返す
        (
            "12345 67890",
            14,
            ("    12345", "        67890"),
        ),
        # 4. 継続行もさらに折り返す
        (
            "This is a very long description.",
            20,
            (
                "    This is a very",
                "        long",
                "        description.",
            ),
        ),
        # 5. 長い単語は分割しない
        (
            "This-is-a-very-long-word",
            10,
            ("    This-is-a-very-long-word",),
        ),
    ],
)
def test_wrap_docstring_item(
    text: str,
    line_length: int,
    expected: tuple[str, ...],
) -> None:
    result = wrap_docstring_item(
        text,
        line_length=line_length,
        first_line_indent=4,
        continuation_indent=8,
    )

    assert result == expected


@pytest.mark.parametrize(
    ("text", "line_length", "expected", "declaration_indent"),
    [
        ("12345 67890", 11, ("12345", "67890"), 0),
        ("12345 67890", 10, ("12345", "67890"), 0),
        (
            "This is a very long description.",
            15,
            ("This is a", "very long", "description."),
            0,
        ),
        ("This-is-a-very-long-word", 10, ("This-is-a-very-long-word",), 0),
        (
            "This is a very long description.",
            15,
            ("This is", "a very long", "description."),
            4,
        ),
        (
            "This is a very long description.",
            15,
            ("This", "is a", "very", "long", "description."),
            8,
        ),
        (
            "First line.\nSecond line.",
            15,
            ("First line.", "Second line."),
            0,
        ),
        (
            "First line.\nThis is a very long second line.",
            15,
            (
                "First line.",
                "This is a very",
                "long second",
                "line.",
            ),
            0,
        ),
        (
            "First paragraph.\n\nSecond paragraph.",
            30,
            (
                "First paragraph.",
                "",
                "Second paragraph.",
            ),
            0,
        ),
    ],
)
def test_render_item_summary(
    text: str, line_length: int, expected: tuple[str, ...], declaration_indent: int
) -> None:
    updated = create_updated_docstring(summary=text, indent=declaration_indent)

    result = render_docstring_lines(updated, line_length)
    expected_value: tuple[DocstringLine, ...] = tuple(
        DocstringBlank() if item == "" else DocstringText(text=item)
        for item in expected
    )
    assert result == expected_value


@pytest.mark.parametrize(
    ("text", "line_length", "expected", "declaration_indent"),
    [
        ("12345 67890", 11, ("12345 67890",), 0),
        ("12345 67890", 10, ("12345", "67890"), 0),
        (
            "This is a very long description.",
            15,
            ("This is a very", "long", "description."),
            0,
        ),
        ("This-is-a-very-long-word", 10, ("This-is-a-very-long-word",), 0),
        (
            "This is a very long description.",
            15,
            ("This is a", "very long", "description."),
            4,
        ),
        (
            "This is a very long description.",
            15,
            ("This is", "a very", "long", "description."),
            8,
        ),
        (
            "First line.\nSecond line.",
            15,
            ("First line.", "Second line."),
            0,
        ),
        (
            "First line.\nThis is a very long second line.",
            15,
            (
                "First line.",
                "This is a very",
                "long second",
                "line.",
            ),
            0,
        ),
        (
            "First paragraph.\n\nSecond paragraph.",
            30,
            (
                "First paragraph.",
                "",
                "Second paragraph.",
            ),
            0,
        ),
    ],
)
def test_render_item_description(
    text: str, line_length: int, expected: tuple[str, ...], declaration_indent: int
) -> None:
    updated = create_updated_docstring(
        summary="text", description=text, indent=declaration_indent
    )

    result = render_docstring_lines(updated, line_length)
    expected_value: list[DocstringLine] = [
        DocstringText(text="text"),
        DocstringBlank(),
    ]
    for item in expected:
        if item == "":
            expected_value.append(DocstringBlank())
        else:
            expected_value.append(DocstringText(text=item))

    assert result == tuple(expected_value)


@pytest.mark.parametrize(
    ("type", "text", "line_length", "expected", "declaration_indent"),
    [
        (
            "User",
            "12345 67890",
            20,
            ("    User: 12345", "        67890"),
            0,
        ),
        (
            "User",
            "12345 67890",
            14,
            (
                "    User:",
                "        12345",
                "        67890",
            ),
            0,
        ),
        (
            "User",
            "This is a very long description.",
            20,
            (
                "    User: This is a",
                "        very long",
                "        description.",
            ),
            0,
        ),
        (
            "User",
            "This-is-a-very-long-word",
            10,
            ("    User:", "        This-is-a-very-long-word"),
            0,
        ),
        (
            "User",
            "This is a very long description.",
            20,
            (
                "    User: This",
                "        is a",
                "        very",
                "        long",
                "        description.",
            ),
            4,
        ),
        (
            "User",
            "This is a very long description.",
            20,
            (
                "    User:",
                "        This",
                "        is a",
                "        very",
                "        long",
                "        description.",
            ),
            8,
        ),
        (
            "User",
            "First line.\nSecond line.",
            30,
            (
                "    User: First line.",
                "        Second line.",
            ),
            0,
        ),
        (
            "User",
            "First line.\nThis is a very long second line.",
            30,
            (
                "    User: First line.",
                "        This is a very long",
                "        second line.",
            ),
            0,
        ),
        (
            "User",
            "First paragraph.\n\nSecond paragraph.",
            30,
            (
                "    User: First paragraph.",
                "",
                "        Second paragraph.",
            ),
            0,
        ),
    ],
)
def test_render_item_return(
    type: str,
    text: str,
    line_length: int,
    expected: tuple[str, ...],
    declaration_indent: int,
) -> None:
    updated = create_updated_docstring(
        summary="text",
        sections=(
            DocstringReturnsSection(
                item=DocstringReturnsSectionItem(
                    type=type,
                    description=text,
                ),
            ),
        ),
        indent=declaration_indent,
    )

    result = render_docstring_lines(updated, line_length)
    expected_value: list[DocstringLine] = [
        DocstringText(text="text"),
        DocstringBlank(),
        DocstringSectionItem(text="Returns:"),
    ]
    for item in expected:
        if item == "":
            expected_value.append(DocstringBlank())
        else:
            expected_value.append(DocstringText(text=item))

    assert result == tuple(expected_value)


@pytest.mark.parametrize(
    ("type", "text", "line_length", "expected", "declaration_indent"),
    [
        (
            "User",
            "12345 67890",
            20,
            ("    User: 12345", "        67890"),
            0,
        ),
        (
            "User",
            "12345 67890",
            14,
            (
                "    User:",
                "        12345",
                "        67890",
            ),
            0,
        ),
        (
            "User",
            "This is a very long description.",
            20,
            (
                "    User: This is a",
                "        very long",
                "        description.",
            ),
            0,
        ),
        (
            "User",
            "This-is-a-very-long-word",
            10,
            ("    User:", "        This-is-a-very-long-word"),
            0,
        ),
        (
            "User",
            "This is a very long description.",
            20,
            (
                "    User: This",
                "        is a",
                "        very",
                "        long",
                "        description.",
            ),
            4,
        ),
        (
            "User",
            "This is a very long description.",
            20,
            (
                "    User:",
                "        This",
                "        is a",
                "        very",
                "        long",
                "        description.",
            ),
            8,
        ),
        (
            "User",
            "First line.\nSecond line.",
            30,
            (
                "    User: First line.",
                "        Second line.",
            ),
            0,
        ),
        (
            "User",
            "First line.\nThis is a very long second line.",
            30,
            (
                "    User: First line.",
                "        This is a very long",
                "        second line.",
            ),
            0,
        ),
        (
            "User",
            "First paragraph.\n\nSecond paragraph.",
            30,
            (
                "    User: First paragraph.",
                "",
                "        Second paragraph.",
            ),
            0,
        ),
    ],
)
def test_render_item_raises(
    type: str,
    text: str,
    line_length: int,
    expected: tuple[str, ...],
    declaration_indent: int,
) -> None:
    updated = create_updated_docstring(
        summary="text",
        sections=(
            DocstringRaisesSection(
                items=(
                    DocstringRaisesSectionItem(
                        type=type,
                        description=text,
                    ),
                )
            ),
        ),
        indent=declaration_indent,
    )

    result = render_docstring_lines(updated, line_length)
    expected_value: list[DocstringLine] = [
        DocstringText(text="text"),
        DocstringBlank(),
        DocstringSectionItem(text="Raises:"),
    ]
    for item in expected:
        if item == "":
            expected_value.append(DocstringBlank())
        else:
            expected_value.append(DocstringText(text=item))

    assert result == tuple(expected_value)


@pytest.mark.parametrize(
    ("text", "line_length", "expected", "declaration_indent"),
    [
        (
            "12345 67890",
            20,
            ("    User: 12345", "        67890"),
            0,
        ),
        (
            "12345 67890",
            14,
            (
                "    User:",
                "        12345",
                "        67890",
            ),
            0,
        ),
        (
            "This is a very long description.",
            20,
            (
                "    User: This is a",
                "        very long",
                "        description.",
            ),
            0,
        ),
        (
            "This-is-a-very-long-word",
            10,
            ("    User:", "        This-is-a-very-long-word"),
            0,
        ),
        (
            "This is a very long description.",
            20,
            (
                "    User: This",
                "        is a",
                "        very",
                "        long",
                "        description.",
            ),
            4,
        ),
        (
            "This is a very long description.",
            20,
            (
                "    User:",
                "        This",
                "        is a",
                "        very",
                "        long",
                "        description.",
            ),
            8,
        ),
        (
            "First line.\nSecond line.",
            30,
            (
                "    User: First line.",
                "        Second line.",
            ),
            0,
        ),
        (
            "First line.\nThis is a very long second line.",
            30,
            (
                "    User: First line.",
                "        This is a very long",
                "        second line.",
            ),
            0,
        ),
        (
            "First paragraph.\n\nSecond paragraph.",
            30,
            (
                "    User: First paragraph.",
                "",
                "        Second paragraph.",
            ),
            0,
        ),
    ],
)
def test_render_item_args(
    text: str,
    line_length: int,
    expected: tuple[str, ...],
    declaration_indent: int,
) -> None:
    updated = create_updated_docstring(
        summary="text",
        sections=(
            DocstringParametersSection(
                items=(
                    DocstringParametersSectionItem(
                        type=None,
                        name="User",
                        description=text,
                    ),
                )
            ),
        ),
        indent=declaration_indent,
    )

    result = render_docstring_lines(updated, line_length)
    expected_value: list[DocstringLine] = [
        DocstringText(text="text"),
        DocstringBlank(),
        DocstringSectionItem(text="Args:"),
    ]
    for item in expected:
        if item == "":
            expected_value.append(DocstringBlank())
        else:
            expected_value.append(DocstringText(text=item))

    assert result == tuple(expected_value)


@pytest.mark.parametrize(
    ("text", "line_length", "expected", "declaration_indent"),
    [
        (
            "12345 67890",
            20,
            ("    12345 67890",),
            0,
        ),
        (
            "12345 67890",
            14,
            (
                "    12345",
                "    67890",
            ),
            0,
        ),
        (
            "This is a very long description.",
            20,
            ("    This is a very", "    long", "    description."),
            0,
        ),
        (
            "This-is-a-very-long-word",
            10,
            ("    This-is-a-very-long-word",),
            0,
        ),
        (
            "This is a very long description.",
            20,
            (
                "    This is a",
                "    very long",
                "    description.",
            ),
            4,
        ),
        (
            "This is a very long description.",
            20,
            (
                "    This is",
                "    a very",
                "    long",
                "    description.",
            ),
            8,
        ),
        (
            "First line.\nSecond line.",
            30,
            (
                "    First line.",
                "    Second line.",
            ),
            0,
        ),
        (
            "First line.\nThis is a very long second line.",
            30,
            (
                "    First line.",
                "    This is a very long second",
                "    line.",
            ),
            0,
        ),
        (
            "First paragraph.\n\nSecond paragraph.",
            30,
            (
                "    First paragraph.",
                "",
                "    Second paragraph.",
            ),
            0,
        ),
    ],
)
def test_render_item_gyomu_context(
    text: str,
    line_length: int,
    expected: tuple[str, ...],
    declaration_indent: int,
) -> None:
    updated = create_updated_docstring(
        summary="text",
        sections=(DocstringGyomuContextSection(value=text),),
        indent=declaration_indent,
    )

    result = render_docstring_lines(updated, line_length)
    expected_value: list[DocstringLine] = [
        DocstringText(text="text"),
        DocstringBlank(),
        DocstringSectionItem(text="Gyomu Context:"),
    ]
    for item in expected:
        if item == "":
            expected_value.append(DocstringBlank())
        else:
            expected_value.append(DocstringText(text=item))

    assert result == tuple(expected_value)


@pytest.mark.parametrize(
    ("summary", "line_length", "expected"),
    [
        (
            "123456789012345 7",
            20,
            ("123456789012345 7",),
        ),
        (
            "1234567890123456 8",
            20,
            ("1234567890123456", "8"),
        ),
        (
            "This is a summary that is long enough to wrap.",
            20,
            (
                "This is a summary",
                "that is long enough",
                "to wrap.",
            ),
        ),
    ],
)
def test_wrap_docstring_summary(
    summary: str,
    line_length: int,
    expected: tuple[str, ...],
) -> None:
    assert (
        wrap_docstring_summary(
            summary,
            line_length=line_length,
        )
        == expected
    )
