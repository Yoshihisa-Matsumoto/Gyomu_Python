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
    ATTR = "attr"
    NAME = "name"
    LAMBDA = "lambda"


class LiteralParameter(BaseModel):
    kind: Literal[ParameterExpressionType.LITERAL] = ParameterExpressionType.LITERAL
    value: str | bytes | bool | int | float | complex | None


class NoneParameter(BaseModel):
    kind: Literal[ParameterExpressionType.NONE] = ParameterExpressionType.NONE


class NameParameter(BaseModel):
    kind: Literal[ParameterExpressionType.NAME] = ParameterExpressionType.NAME
    name: str


class AttributeParameter(BaseModel):
    kind: Literal[ParameterExpressionType.ATTR] = ParameterExpressionType.ATTR
    value: Parameter
    attribute: str


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


class Argument(BaseModel):
    arg: str
    annotation: Parameter


class Arguments(BaseModel):
    posonlyargs: tuple[Argument, ...]
    args: tuple[Argument, ...]
    vararg: Argument | None
    kwonlyargs: tuple[Argument, ...]
    kw_defaults: tuple[Parameter, ...]
    kwarg: Argument | None
    defaults: tuple[Parameter, ...]


class LambdaParameter(BaseModel):
    kind: Literal[ParameterExpressionType.LAMBDA] = ParameterExpressionType.LAMBDA
    args: Arguments
    body: Parameter


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
    | NameParameter
    | CallParameter
    | TupleParameter
    | ListParameter
    | DictParameter
    | AttributeParameter
    | LambdaParameter,
    Field(discriminator="kind"),
]


class ParameterDefault(BaseModel):
    name: str
    value: Parameter | None


class ModelDefault(BaseModel):
    class_name: str
    parameters: tuple[ParameterDefault, ...]


class ModelDefaults(BaseModel):
    models: tuple[ModelDefault, ...]
