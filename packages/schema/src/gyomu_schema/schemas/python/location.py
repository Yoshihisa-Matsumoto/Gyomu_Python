from pydantic import BaseModel


class SourceLocation(BaseModel):
    """Represents a location within a source file.

    Gyomu Context:
        Line numbers are 1-based, following the convention used by Griffe.

        Column offsets are 0-based character offsets within a line.

        Source offsets are 0-based character offsets within the entire
        source string.

        Both column ranges and source ranges use half-open intervals
        ``[start, end)``. Therefore, the end position points immediately
        after the last character of the represented source range.

        For example, given the following source::

            VERSION = 5

        the location of ``VERSION = 5`` is represented as::

            start_line = 1
            start_column = 0
            end_line = 1
            end_column = 11

        and ``start_offset`` / ``end_offset`` represent the same range
        within the complete source string.

        For an indented symbol, leading indentation is excluded from the
        symbol range.

        Source locations are intended to preserve the exact source range
        needed for future source transformations, such as safely updating
        documentation without modifying surrounding comments, whitespace,
        indentation, or blank lines.
    """

    start_line: int
    """Starting line number (1-based)."""

    start_column: int
    """Starting column offset (0-based)."""

    start_offset: int
    """Starting character offset in the source string (0-based)."""

    end_line: int
    """Ending line number (1-based)."""

    end_column: int
    """Ending column offset (0-based)."""

    end_offset: int
    """Ending character offset in the source string (0-based)."""
