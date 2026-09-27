import traceback
from dataclasses import fields, is_dataclass
from pprint import pformat

from pydantic import BaseModel

# def format_object(value: object) -> str:
#     if is_dataclass(value) and not isinstance(value, type):
#         return pformat(asdict(value))

#     return pformat(vars(value)) if hasattr(value, "__dict__") else repr(value)


def format_object(value: object, *, depth: int = 3) -> str:
    """Format an object into a pretty-printed string.

    Formats an object into a pretty-printed string representation.

    Args:
        value (object): The object to format.
        depth (int): Maximum recursion depth for formatting nested structures.

    Returns:
        str: A pretty-printed string representation of the object.
    """
    return pformat(_format_value(value, depth))


def _format_value(value: object, depth: int) -> object:
    """Recursively format a value for display.

    Recursively formats a value for pretty-printing up to a given depth limit.

    Args:
        value (object): The value to format.
        depth (int): The maximum recursion depth allowed.

    Returns:
        object: The formatted representation of the value.
    """
    if isinstance(value, (str, int, float, bool, type(None))):
        return value

    if depth <= 0:
        return f"<{type(value).__name__} ...>"

    if isinstance(value, BaseException):
        result: dict[str, object] = {
            key: _format_value(item, depth - 1) for key, item in vars(value).items()
        }
        if value.args:
            result["args"] = _format_value(value.args, depth - 1)
        if value.__cause__ is not None:
            result["cause"] = _format_value(value.__cause__, depth - 1)

        if value.__traceback__ is not None:
            result["traceback"] = "".join(traceback.format_exception(value))
        return result

    if isinstance(value, BaseModel):
        return {
            key: _format_value(item, depth - 1)
            for key, item in value.model_dump().items()
        }

    if is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: _format_value(getattr(value, field.name), depth - 1)
            for field in fields(value)
        }

    if isinstance(value, dict):
        return {key: _format_value(item, depth - 1) for key, item in value.items()}

    if isinstance(value, (list, tuple, set, frozenset)):
        return [_format_value(item, depth - 1) for item in value]

    if hasattr(value, "__dict__"):
        return {
            key: _format_value(item, depth - 1) for key, item in vars(value).items()
        }

    return value
