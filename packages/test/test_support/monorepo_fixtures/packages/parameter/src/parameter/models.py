
from dataclasses import dataclass
from enum import Enum
from typing import Literal

from pydantic import BaseModel


class Color(Enum):
    RED = "red"
    BLUE = "blue"


class StringLiteralModel(BaseModel):
    value: str


class IntegerLiteralModel(BaseModel):
    value: int


class BooleanLiteralModel(BaseModel):
    value: bool


class NoneDefaultModel(BaseModel):
    value: str | None


class NameReferenceModel(BaseModel):
    value: str


class AttributeReferenceModel(BaseModel):
    value: Literal[Color.BLUE]


class EmptyTupleModel(BaseModel):
    value: tuple[str, ...]


class TupleLiteralModel(BaseModel):
    value: tuple[int, ...]


class SingletonTupleModel(BaseModel):
    value: tuple[int, ...]


class ListLiteralModel(BaseModel):
    value: list[int]


class DictLiteralModel(BaseModel):
    value: dict[str, int]


class BasicModel(BaseModel):
    value: str


class CallDefaultModel(BaseModel):
    value: BasicModel


class KeywordCallModel(BaseModel):
    value: BasicModel


class NestedCallModel(BaseModel):
    value: tuple[BasicModel, ...]

@dataclass
class RequiredParameterModel:
    user_id: int
    name: str
