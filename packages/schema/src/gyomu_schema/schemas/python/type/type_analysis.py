from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

# from gyomu_schema.schemas.python.type.generics import GenericsParameter
from gyomu_schema.schemas.python.type.structure import (
    NameStructureAnalysis,
    NoneStructureAnalysis,
    TypeStructureKind,
    UnknownStructureAnalysis,
)


class TypeAnalysis(BaseModel):
    text: str
    structure: TypeStructureAnalysis | None = None
    generics: tuple[GenericsParameter, ...] | None = None


class GenericsParameter(BaseModel):
    name: str
    type: TypeAnalysis | None = None


class UnionStructureAnalysis(BaseModel):
    kind: Literal[TypeStructureKind.UNION] = TypeStructureKind.UNION
    types: tuple[TypeAnalysis, ...]


type TypeStructureAnalysis = (
    NameStructureAnalysis
    | NoneStructureAnalysis
    | UnionStructureAnalysis
    # | GenericStructureAnalysis
    # | LiteralStructureAnalysis
    # | CallableStructureAnalysis
    | UnknownStructureAnalysis
)
