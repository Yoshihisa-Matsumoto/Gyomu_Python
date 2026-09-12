from __future__ import annotations

from datetime import datetime as DateTime
from enum import Enum
from typing import TypeAlias


class User:
    pass


class Outer:
    class Inner:
        pass


class Color(Enum):
    RED = "red"


class Box[U]:
    value: U


T = int
UserId: TypeAlias = int


value_builtin: int
value_custom: User
value_nested: Outer.Inner

value_alias: T
value_type_alias: UserId

value_module: str
value_enum_class: Color
value_enum_member: Color.RED
value_enum_value: Color.RED.value

value_generic: list[int]
value_union: int | None | str
value: DateTime
