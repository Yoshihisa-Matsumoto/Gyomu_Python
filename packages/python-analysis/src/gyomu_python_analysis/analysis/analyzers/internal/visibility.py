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


def calculate_visibility(name: str) -> Visibility:
    if name in _SPECIAL_NAMES:
        return Visibility.SPECIAL

    if name.startswith("_"):
        return Visibility.PRIVATE

    return Visibility.PUBLIC
