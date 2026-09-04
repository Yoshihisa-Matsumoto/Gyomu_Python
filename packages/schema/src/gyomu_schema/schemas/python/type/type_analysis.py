from __future__ import annotations

from collections.abc import Sequence
from typing import Literal

from pydantic import BaseModel

# from gyomu_schema.schemas.python.type.generics import GenericsParameter
from gyomu_schema.schemas.python.type.structure import (
    LiteralValue,
    NameStructureAnalysis,
    NoneStructureAnalysis,
    TypeStructureKind,
    UnknownStructureAnalysis,
)


class TypeAnalysis(BaseModel):
    text: str
    structure: ExpressionAnalysis | None = None


# class GenericsParameter(BaseModel):
#     name: str
#     type: TypeAnalysis | None = None


class UnionStructureAnalysis(BaseModel):
    kind: Literal[TypeStructureKind.UNION] = TypeStructureKind.UNION
    types: tuple[TypeExpression, ...]


class AttributeStructureAnalysis(BaseModel):
    kind: TypeStructureKind = TypeStructureKind.ATTRIBUTE
    values: tuple[TypeExpression, ...]


class TupleStructureAnalysis(BaseModel):
    kind: TypeStructureKind = TypeStructureKind.TUPLE
    elements: Sequence[TypeExpression]
    variable_length: bool = False


class SetStructureAnalysis(BaseModel):
    kind: TypeStructureKind = TypeStructureKind.SET
    element_type: TypeExpression


class LiteralStructureAnalysis(BaseModel):
    kind: TypeStructureKind = TypeStructureKind.LITERAL
    value: TypeExpression


class ArrayStructureAnalysis(BaseModel):
    kind: TypeStructureKind = TypeStructureKind.ARRAY
    element: TypeExpression


class DictionaryStructureAnalysis(BaseModel):
    kind: TypeStructureKind = TypeStructureKind.DICTIONARY
    keys: TypeExpression
    values: TypeExpression


class CallableStructureAnalysis(BaseModel):
    kind: TypeStructureKind = TypeStructureKind.CALLABLE
    parameters: tuple[TypeExpression, ...] | None
    return_type: TypeExpression


class GenericsStructureAnalysis(BaseModel):
    kind: TypeStructureKind = TypeStructureKind.GENERIC
    base: TypeExpression
    parameters: tuple[TypeExpression, ...]


type ExpressionAnalysis = (
    NameStructureAnalysis
    | NoneStructureAnalysis
    | UnionStructureAnalysis
    | AttributeStructureAnalysis
    | TupleStructureAnalysis
    | GenericsStructureAnalysis
    | LiteralStructureAnalysis
    | ArrayStructureAnalysis
    | DictionaryStructureAnalysis
    | CallableStructureAnalysis
    | UnknownStructureAnalysis
    | SetStructureAnalysis
)

type TypeExpression = LiteralValue | ExpressionAnalysis
