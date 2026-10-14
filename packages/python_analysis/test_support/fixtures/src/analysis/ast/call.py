

from typing import Any


def combine(*values: Any, **options: Any) -> Any:
    return values, options


def convert(value: int) -> str:
    return str(value)


def create_value(value: int) -> str:
    return str(value)


def build_option(value: int = 0) -> dict[str, int]:
    return {"value": value}


class Service:
    def execute(self, *args: Any, **kwargs: Any) -> Any:
        return args, kwargs


service = Service()


def simple_call(value: int) -> str:
    return convert(value)


def positional_call(value: int) -> Any:
    return combine(value, convert(value))


def keyword_call(value: int) -> Any:
    return combine(value, prefix="value", suffix="!")


def attribute_call(value: int) -> Any:
    return service.execute(value)


def nested_call(value: int) -> Any:
    return service.execute(
        create_value(value),
        option=build_option(value),
    )


def starred_call(values: list[int]) -> Any:
    return combine(*values)


def double_starred_call(options: dict[str, Any]) -> Any:
    return combine(**options)


def complex_call(value: int, values: list[int]) -> Any:
    return service.execute(
        convert(value),
        *values,
        option=build_option(value),
        **{"value": value},
    )
