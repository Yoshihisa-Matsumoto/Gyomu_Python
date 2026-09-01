from pydantic import BaseModel


class SourceLocation(BaseModel):
    """Represents a location within a source file.

    Gyomu Context:
        Line numbers are 1-based, following the convention used by Griffe.

        Column offsets are 0-based character offsets within a line.

        The start position is inclusive and the end position is exclusive.
        Therefore, the source range is represented as a half-open interval
        ``[start, end)``.

        For example, given the following source line::

            VERSION = 5

        the location of ``VERSION = 5`` is represented as::

            start_column = 0
            end_column = 11

        For an indented symbol, leading indentation is excluded from the
        symbol range. For example::

                VERSION = 5

        has ``start_column = 4``.

        The end column points immediately after the last character of the
        symbol. This makes the location directly usable with Python string
        slicing.

        Source locations are intended to preserve the exact source range
        needed for future source transformations, such as safely updating
        documentation without modifying surrounding comments, whitespace,
        indentation, or blank lines.
    """

    start_line: int
    start_column: int
    end_line: int
    end_column: int
