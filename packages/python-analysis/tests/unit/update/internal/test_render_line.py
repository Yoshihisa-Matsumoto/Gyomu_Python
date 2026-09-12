from gyomu_python_analysis.update.docstring.line import (
    DocstringBlank,
    DocstringSectionItem,
    DocstringText,
)
from gyomu_python_analysis.update.docstring.updated_docstring import UpdatedDocstring
from gyomu_python_analysis.update.internal.render_line import render_docstring_lines
from gyomu_schema.schemas.python.docstring import (
    DocstringAnalysis,
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

from tests.helpers import _default_identity, create_location


def create_updated_docstring(
    summary: str | None,
    description: str | None = None,
    sections: tuple[DocstringSection, ...] | None = None,
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
            indent=4,
        ),
    )


def test_renders_summary() -> None:
    updated = create_updated_docstring(
        summary="Finds a user.",
    )

    result = render_docstring_lines(updated)

    assert result == (DocstringText("Finds a user."),)


def test_renders_summary_and_description() -> None:
    updated = create_updated_docstring(
        summary="Finds a user.",
        description="Searches the repository.",
    )

    result = render_docstring_lines(updated)

    assert result == (
        DocstringText("Finds a user."),
        DocstringBlank(),
        DocstringText("Searches the repository."),
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

    result = render_docstring_lines(updated)

    assert result == (
        DocstringBlank(),
        DocstringSectionItem("Args:"),
        DocstringText("    user_id (int): User identifier."),
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

    result = render_docstring_lines(updated)

    assert result == (
        DocstringText("Finds a user."),
        DocstringBlank(),
        DocstringSectionItem("Args:"),
        DocstringText("    user_id (int): User identifier."),
        DocstringText("    name: User name."),
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

    result = render_docstring_lines(updated)

    assert result == (
        DocstringText("Finds a user."),
        DocstringBlank(),
        DocstringSectionItem("Returns:"),
        DocstringText("    User: The matching user."),
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

    result = render_docstring_lines(updated)

    assert result == (
        DocstringText("Finds a user."),
        DocstringBlank(),
        DocstringSectionItem("Returns:"),
        DocstringText("    The matching user."),
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

    result = render_docstring_lines(updated)

    assert result == (
        DocstringText("Finds a user."),
        DocstringBlank(),
        DocstringSectionItem("Raises:"),
        DocstringText(
            "    ValueError: If the user does not exist.",
        ),
    )


def test_renders_raises_without_type() -> None:
    updated = create_updated_docstring(
        summary="Finds a user.",
        sections=(
            DocstringRaisesSection(
                items=(
                    DocstringRaisesSectionItem(
                        type=None,
                        description="If the user does not exist.",
                    ),
                ),
            ),
        ),
    )

    result = render_docstring_lines(updated)

    assert result == (
        DocstringText("Finds a user."),
        DocstringBlank(),
        DocstringSectionItem("Raises:"),
        DocstringText(
            "    If the user does not exist.",
        ),
    )


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

    result = render_docstring_lines(updated)

    assert result == (
        DocstringText("Finds a user."),
        DocstringBlank(),
        DocstringSectionItem("Raises:"),
        DocstringText(
            "    ValueError: If the user does not exist.",
        ),
        DocstringText(
            "    PermissionError: If access is denied.",
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

    result = render_docstring_lines(updated)

    assert result == (
        DocstringText("Finds a user."),
        DocstringBlank(),
        DocstringText("Searches the repository."),
        DocstringBlank(),
        DocstringSectionItem("Args:"),
        DocstringText("    user_id (int): User identifier."),
        DocstringText("    name: User name."),
        DocstringBlank(),
        DocstringSectionItem("Returns:"),
        DocstringText("    User: The matching user."),
        DocstringBlank(),
        DocstringSectionItem("Raises:"),
        DocstringText(
            "    ValueError: If the user does not exist.",
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

    result = render_docstring_lines(updated)

    assert result == (
        DocstringText("Finds a user."),
        DocstringBlank(),
        DocstringSectionItem("Notes:"),
        DocstringText(
            "    This operation uses the repository cache.",
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

    result = render_docstring_lines(updated)

    assert result == (
        DocstringText("Finds a user."),
        DocstringBlank(),
        DocstringSectionItem("Gyomu Context:"),
        DocstringText(
            "    Used by the user lookup workflow.",
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

    result = render_docstring_lines(updated)

    assert result == (
        DocstringText("Finds a user."),
        DocstringBlank(),
        DocstringSectionItem("Warning:"),
        DocstringText(
            "    This operation may be expensive.",
        ),
    )
