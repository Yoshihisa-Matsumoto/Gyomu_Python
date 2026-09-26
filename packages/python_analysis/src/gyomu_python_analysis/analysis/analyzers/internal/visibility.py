from gyomu_schema.schemas.python.visibility import Visibility

_SPECIAL_NAMES = frozenset(
    {
        "__all__",
        "__annotations__",
        "__builtins__",
        "__cached__",
        "__doc__",
        "__file__",
        "__loader__",
        "__name__",
        "__package__",
        "__path__",
        "__spec__",
    }
)
"""Set of special Python module and class names.

Set of special Python module and class names.
"""


def calculate_visibility(name: str) -> Visibility:
    """Calculate the visibility of a symbol name.

    Determines the visibility of a given name based on naming conventions and special
    name lists.

    Args:
        name (str): The name to check.

    Returns:
        Visibility: The calculated visibility level.
    """
    if name in _SPECIAL_NAMES:
        return Visibility.SPECIAL

    if name.startswith("_"):
        return Visibility.PRIVATE

    return Visibility.PUBLIC
