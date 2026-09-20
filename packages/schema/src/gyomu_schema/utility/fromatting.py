from dataclasses import asdict, is_dataclass
from pprint import pformat


def format_object(value: object) -> str:
    if is_dataclass(value) and not isinstance(value, type):
        return pformat(asdict(value))

    return pformat(vars(value)) if hasattr(value, "__dict__") else repr(value)
