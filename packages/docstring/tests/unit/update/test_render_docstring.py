from gyomu_docstring.update.docstring.rendered_symbol import (
    RenderedSymbolDocstring,
)
from gyomu_docstring.update.docstring.updated_docstring import UpdatedDocstring
from gyomu_docstring.update.render_docstring import render_docstring
from gyomu_schema.schemas.python.docstring import (
    DocstringAnalysis,
    DocstringSection,
    DocstringStyle,
)

from packages.docstring.docstring_test_support.helper import _default_identity
from packages.schema.schema_test_support.helpers import create_location


def make_updated_docstring(
    summary: str | None,
    indent: int,
    start_offset: int,
    end_offset: int,
    description: str | None = None,
    sections: tuple[DocstringSection, ...] | None = None,
    start_line: int = 1,
    end_line: int = 1,
    start_column: int = 0,
    end_column: int = 0,
) -> UpdatedDocstring:
    return UpdatedDocstring(
        identity=_default_identity,
        docstring=DocstringAnalysis(
            summary=summary,
            description=description,
            style=DocstringStyle.GOOGLE,
            location=create_location(
                start_offset=start_offset,
                end_offset=end_offset,
                start_line=start_line,
                start_column=start_column,
                end_line=end_line,
                end_column=end_column,
            ),
            sections=sections if sections is not None else tuple(),
            raw="",
            indent=indent,
        ),
    )


class TestRenderDocstring:
    def test_renders_existing_docstring(self) -> None:
        updated = make_updated_docstring(
            summary="Finds a user.",
            indent=4,
            start_offset=100,
            end_offset=125,
        )

        result = render_docstring(updated)

        assert isinstance(result, RenderedSymbolDocstring)
        assert result.identity == updated.identity
        assert result.docstring == '    """Finds a user."""'
        assert result.location.start_offset == 96
        assert result.location.end_offset == 125

    def test_renders_added_docstring(self) -> None:
        updated = make_updated_docstring(
            summary="Finds a user.",
            indent=4,
            start_offset=100,
            end_offset=100,
        )

        result = render_docstring(updated)

        assert result.identity == updated.identity
        assert result.docstring == '    """Finds a user."""\n'
        assert result.location.start_offset == 96
        assert result.location.end_offset == 96

    def test_adjusts_start_offset_by_indent(self) -> None:
        updated = make_updated_docstring(
            summary="Finds a user.",
            indent=8,
            start_offset=200,
            end_offset=220,
        )

        result = render_docstring(updated)

        assert result.location.start_offset == 192

    def test_does_not_adjust_end_offset_for_existing_docstring(
        self,
    ) -> None:
        updated = make_updated_docstring(
            summary="Finds a user.",
            indent=8,
            start_offset=200,
            end_offset=220,
        )

        result = render_docstring(updated)

        assert result.location.end_offset == 220

    def test_adjusts_end_offset_for_added_docstring(self) -> None:
        updated = make_updated_docstring(
            summary="Finds a user.",
            indent=8,
            start_offset=200,
            end_offset=200,
        )

        result = render_docstring(updated)

        assert result.location.end_offset == 192

    def test_preserves_other_location_fields(self) -> None:
        updated = make_updated_docstring(
            summary="Finds a user.",
            indent=4,
            start_offset=100,
            end_offset=125,
            start_line=10,
            start_column=4,
            end_line=12,
            end_column=7,
        )

        result = render_docstring(updated)

        assert result.location.start_line == 10
        assert result.location.start_column == 4
        assert result.location.end_line == 12
        assert result.location.end_column == 7

    def test_returns_rendered_symbol_docstring(self) -> None:
        updated = make_updated_docstring(
            summary="Finds a user.",
            indent=4,
            start_offset=100,
            end_offset=125,
        )

        result = render_docstring(updated)

        assert isinstance(result, RenderedSymbolDocstring)
