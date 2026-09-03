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
    generics: tuple[GenericsParameter, ...] | None = None


class GenericsParameter(BaseModel):
    name: str
    type: TypeAnalysis | None = None


class UnionStructureAnalysis(BaseModel):
    kind: Literal[TypeStructureKind.UNION] = TypeStructureKind.UNION
    types: tuple[TypeAnalysis, ...]


class AttributeStructureAnalysis(BaseModel):
    kind: TypeStructureKind = TypeStructureKind.ATTRIBUTE
    values: tuple[TypeAnalysis, ...]


class TupleStructureAnalysis(BaseModel):
    kind: TypeStructureKind = TypeStructureKind.TUPLE
    elements: Sequence[TypeExpression]


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
    parameters: tuple[TypeAnalysis, ...] | None
    return_type: TypeAnalysis


type ExpressionAnalysis = (
    NameStructureAnalysis
    | NoneStructureAnalysis
    | UnionStructureAnalysis
    | AttributeStructureAnalysis
    | TupleStructureAnalysis
    # | GenericStructureAnalysis
    | LiteralStructureAnalysis
    | ArrayStructureAnalysis
    | DictionaryStructureAnalysis
    | CallableStructureAnalysis
    | UnknownStructureAnalysis
)

type TypeExpression = LiteralValue | ExpressionAnalysis
