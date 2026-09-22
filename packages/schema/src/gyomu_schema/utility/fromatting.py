from dataclasses import fields, is_dataclass
from pprint import pformat

from pydantic import BaseModel

# def format_object(value: object) -> str:
#     if is_dataclass(value) and not isinstance(value, type):
#         return pformat(asdict(value))

#     return pformat(vars(value)) if hasattr(value, "__dict__") else repr(value)


def format_object(value: object, *, depth: int = 3) -> str:
    return pformat(_format_value(value, depth))


def _format_value(value: object, depth: int) -> object:
    if isinstance(value, (str, int, float, bool, type(None))):
        return value

    if depth <= 0:
        return f"<{type(value).__name__} ...>"

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
