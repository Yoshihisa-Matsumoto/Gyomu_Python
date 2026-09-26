from gyomu_docstring.update.docstring.rendered_symbol import (
    RenderedSymbolDocstring,
)
from gyomu_docstring.update.docstring.updated_docstring import UpdatedDocstring
from gyomu_docstring.update.internal.render_line import render_docstring_lines
from gyomu_docstring.update.internal.render_string import render_docstring_string


def render_docstring(
    updated: UpdatedDocstring, formatter_line_length: int
) -> RenderedSymbolDocstring:
    """Renders an updated docstring.

    Renders an updated docstring into its final formatted string representation along
    with its source code location.

    Args:
        updated (UpdatedDocstring): The updated docstring data to render.
        formatter_line_length: int (int): Maximum line length constraint for the
            formatter.

    Returns:
        RenderedSymbolDocstring: The rendered symbol docstring structure with location
            and text.
    """
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
    """Renders multiple updated docstrings.

    Renders a collection of updated docstrings into their final formatted
    representations.

    Args:
        updated_list (tuple[UpdatedDocstring, ...]): A tuple of updated docstrings to
            render.
        formatter_line_length: int (int): Maximum line length constraint for the
            formatter.

    Returns:
        tuple[RenderedSymbolDocstring, ...]: A tuple of rendered symbol docstrings.
    """
    return tuple(
        render_docstring(updated, formatter_line_length) for updated in updated_list
    )
