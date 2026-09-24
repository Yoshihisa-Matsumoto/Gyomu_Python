from enum import StrEnum


class Visibility(StrEnum):
    """Visibility levels for Python schema elements.

    Enumeration representing visibility levels (public, private, or special).
    """

    PUBLIC = "public"
    """Public visibility.

    Public visibility level.
    """
    PRIVATE = "private"
    """Private visibility.

    Private visibility level.
    """
    SPECIAL = "special"
    """Special visibility.

    Special visibility level.
    """
