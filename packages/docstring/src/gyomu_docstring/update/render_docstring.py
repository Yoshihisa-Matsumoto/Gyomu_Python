from gyomu_docstring.update.docstring.rendered_symbol import (
    RenderedSymbolDocstring,
)
from gyomu_docstring.update.docstring.updated_docstring import UpdatedDocstring
from gyomu_docstring.update.internal.render_line import render_docstring_lines
from gyomu_docstring.update.internal.render_string import render_docstring_string


def render_docstring(
    updated: UpdatedDocstring, formatter_line_length: int
) -> RenderedSymbolDocstring:
    lines = render_docstring_lines(updated, formatter_line_length)

    document = render_docstring_string(
        lines,
        updated.docstring.location.start_offset
        == updated.docstring.location.end_offset,
        updated.docstring.indent,
    )

    is_added = (
        updated.docstring.location.start_offset == updated.docstring.location.end_offset
    )

    location = updated.docstring.location.model_copy()

    if not is_added:
        location.start_offset -= updated.docstring.indent

    if is_added:
        location.end_offset = location.start_offset

    return RenderedSymbolDocstring(
        identity=updated.identity,
        docstring=document,
        location=location,
    )


def render_docstrings(
    updated_list: tuple[UpdatedDocstring, ...], formatter_line_length: int
) -> tuple[RenderedSymbolDocstring, ...]:
    return tuple(
        render_docstring(updated, formatter_line_length) for updated in updated_list
    )
