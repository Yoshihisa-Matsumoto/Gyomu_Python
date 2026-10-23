from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from gyomu_schema.schemas.python.types import DeclarationIdentity


class ParameterExpressionType(StrEnum):
    LITERAL = "literal"
    NONE = "none"
    CALL = "call"
    TUPLE = "tuple"
    LIST = "list"
    DICT = "dict"
    ENUM = "enum"


class LiteralParameter(BaseModel):
    kind: Literal[ParameterExpressionType.LITERAL] = ParameterExpressionType.LITERAL
    value: int | bool | str | float


class NoneParameter(BaseModel):
    kind: Literal[ParameterExpressionType.NONE] = ParameterExpressionType.NONE


class EnumParameter(BaseModel):
    kind: Literal[ParameterExpressionType.ENUM] = ParameterExpressionType.ENUM
    enum_identity: DeclarationIdentity
    member_name: str


class TupleParameter(BaseModel):
    kind: Literal[ParameterExpressionType.TUPLE] = ParameterExpressionType.TUPLE
    elements: tuple[Parameter, ...]


class ListParameter(BaseModel):
    kind: Literal[ParameterExpressionType.LIST] = ParameterExpressionType.LIST
    elements: tuple[Parameter, ...]


class DictEntry(BaseModel):
    key: Parameter
    value: Parameter


class DictParameter(BaseModel):
    kind: Literal[ParameterExpressionType.DICT] = ParameterExpressionType.DICT
    entries: tuple[DictEntry, ...]


class KeywordArgument(BaseModel):
    name: str
    value: Parameter


class CallParameter(BaseModel):
    kind: Literal[ParameterExpressionType.CALL] = ParameterExpressionType.CALL
    callable_identity: DeclarationIdentity
    args: tuple[Parameter, ...] = ()
    kwargs: tuple[KeywordArgument, ...] = ()


type Parameter = Annotated[
    LiteralParameter
    | NoneParameter
    | CallParameter
    | TupleParameter
    | ListParameter
    | DictParameter
    | EnumParameter,
    Field(discriminator="kind"),
]


class ParameterDefault(BaseModel):
    name: str
    value: Parameter


class ModelDefault(BaseModel):
    class_name: str
    parameters: tuple[ParameterDefault, ...]


class ModelDefaults(BaseModel):
    models: tuple[ModelDefault, ...]
