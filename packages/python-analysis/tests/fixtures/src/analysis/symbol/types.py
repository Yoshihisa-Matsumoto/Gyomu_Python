from collections.abc import Callable
from enum import Enum
from typing import Literal


class Color(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


value_int: int
value_str: str
value_none: None
value_custom: Foo
value_list: list[int]
value_dict: dict[str, int]
value_tuple: tuple[str, ...]
value_union: int | None | str | "None"
value_literal_int: Literal[1]
value_literal_int2: Literal[1, 2]
value_literal_str: Literal["a"]
value_literal_str2: Literal["a", "b"]
value_literal_bool: Literal[True]
value_literal_bool2: Literal[True, False, Color.RED]
value_callable: Callable[[Exception], bool]
value_callable2: Callable[[str, bool, dict[str, str]], list[str]]
