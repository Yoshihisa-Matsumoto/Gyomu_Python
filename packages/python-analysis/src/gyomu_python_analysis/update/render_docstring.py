from gyomu_python_analysis.update.docstring.rendered_symbol import (
    RenderedSymbolDocstring,
)
from gyomu_python_analysis.update.docstring.updated_docstring import UpdatedDocstring
from gyomu_python_analysis.update.internal.render_line import render_docstring_lines
from gyomu_python_analysis.update.internal.render_string import render_docstring_string


def render_docstring(updated: UpdatedDocstring) -> RenderedSymbolDocstring:
    lines = render_docstring_lines(updated)

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

    location.start_offset -= updated.docstring.indent

    if is_added:
        location.end_offset -= updated.docstring.indent

    return RenderedSymbolDocstring(
        identity=updated.identity,
        docstring=document,
        location=location,
    )


def render_docstrings(
    updated_list: tuple[UpdatedDocstring, ...],
) -> tuple[RenderedSymbolDocstring, ...]:
    return tuple(render_docstring(updated) for updated in updated_list)
