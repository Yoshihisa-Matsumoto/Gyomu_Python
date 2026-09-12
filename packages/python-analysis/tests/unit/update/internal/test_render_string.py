import pytest
from gyomu_python_analysis.update.docstring.line import (
    DocstringBlank,
    DocstringSectionItem,
    DocstringText,
)
from gyomu_python_analysis.update.internal.render_string import render_docstring_string


class TestRenderDocstringString:
    def test_returns_none_for_empty_lines(self) -> None:
        result = render_docstring_string(
            lines=(),
            is_added=False,
            indent=0,
        )

        assert result is None

    def test_renders_single_line_docstring_without_indent(self) -> None:
        result = render_docstring_string(
            lines=(DocstringText("Finds a user."),),
            is_added=False,
            indent=0,
        )

        assert result == '"""Finds a user."""'

    def test_renders_single_line_docstring_with_indent(self) -> None:
        result = render_docstring_string(
            lines=(DocstringText("Finds a user."),),
            is_added=False,
            indent=4,
        )

        assert result == '    """Finds a user."""'

    # def test_renders_blank_line(self) -> None:
    #     result = render_docstring_string(
    #         lines=(DocstringBlank(),),
    #         is_added=False,
    #         indent=4,
    #     )

    #     assert result == '    """\n    \n    """'

    def test_renders_section(self) -> None:
        result = render_docstring_string(
            lines=(
                DocstringBlank(),
                DocstringSectionItem("Args:"),
            ),
            is_added=False,
            indent=4,
        )

        assert result == '    """\n    Args:\n    """'

    def test_renders_multiline_text(self) -> None:
        result = render_docstring_string(
            lines=(DocstringText("first line\nsecond line"),),
            is_added=False,
            indent=4,
        )

        assert result == ('    """first line\n    second line\n    """')

    def test_renders_multiline_section(self) -> None:
        result = render_docstring_string(
            lines=(
                DocstringBlank(),
                DocstringSectionItem(
                    "Args:\n    user_id: User identifier.",
                ),
            ),
            is_added=False,
            indent=4,
        )

        assert result == (
            '    """\n    Args:\n        user_id: User identifier.\n    """'
        )

    def test_renders_multiple_lines(self) -> None:
        result = render_docstring_string(
            lines=(
                DocstringText("Finds a user."),
                DocstringBlank(),
                DocstringSectionItem("Args:"),
                DocstringText("    user_id (int): User identifier."),
                DocstringBlank(),
                DocstringSectionItem("Returns:"),
                DocstringText("    User: The matching user."),
            ),
            is_added=False,
            indent=4,
        )

        assert result == (
            '    """Finds a user.\n'
            "    \n"
            "    Args:\n"
            "        user_id (int): User identifier.\n"
            "    \n"
            "    Returns:\n"
            "        User: The matching user.\n"
            '    """'
        )

    def test_renders_section_without_summary(self) -> None:
        result = render_docstring_string(
            lines=(
                DocstringBlank(),
                DocstringSectionItem("Args:"),
                DocstringText("    user_id (int): User identifier."),
            ),
            is_added=False,
            indent=4,
        )

        assert result == (
            '    """\n    Args:\n        user_id (int): User identifier.\n    """'
        )

    def test_renders_summary_and_description(self) -> None:
        result = render_docstring_string(
            lines=(
                DocstringText("Finds a user."),
                DocstringBlank(),
                DocstringText("Searches the repository."),
            ),
            is_added=False,
            indent=4,
        )

        assert result == (
            '    """Finds a user.\n    \n    Searches the repository.\n    """'
        )

    def test_adds_trailing_newline_when_added(self) -> None:
        result = render_docstring_string(
            lines=(DocstringText("Finds a user."),),
            is_added=True,
            indent=4,
        )

        assert result == '    """Finds a user."""\n'

    def test_does_not_add_trailing_newline_when_existing(self) -> None:
        result = render_docstring_string(
            lines=(DocstringText("Finds a user."),),
            is_added=False,
            indent=4,
        )

        assert result == '    """Finds a user."""'

    @pytest.mark.parametrize(
        ("indent", "expected_prefix"),
        [
            (0, ""),
            (2, "  "),
            (4, "    "),
            (8, "        "),
        ],
    )
    def test_applies_indent_to_every_physical_line(
        self,
        indent: int,
        expected_prefix: str,
    ) -> None:
        result = render_docstring_string(
            lines=(DocstringText("first\nsecond"),),
            is_added=False,
            indent=indent,
        )

        assert result == (
            f'{expected_prefix}"""first\n{expected_prefix}second\n{expected_prefix}"""'
        )
