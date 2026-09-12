from __future__ import annotations

from typing import Literal, TypedDict

from pydantic import BaseModel

from gyomu_schema.schemas.python.method_analysis import MethodAnalysis
from gyomu_schema.schemas.python.pydantic import PydanticFieldAnalysis
from gyomu_schema.schemas.python.symbol_base import (
    DeclarationKind,
    MemberAnalysisBase,
    SymbolAnalysisBase,
)
from gyomu_schema.schemas.python.type.type_analysis import TypeAnalysis, TypeExpression


class ClassVariableAnalysis(MemberAnalysisBase):
    kind: Literal[DeclarationKind.VARIABLE] = DeclarationKind.VARIABLE
    type: TypeAnalysis | None
    value_source: str | None
    value_expression: TypeExpression | None
    pydantic: PydanticFieldAnalysis | None


class ClassTypeAliasAnalysis(MemberAnalysisBase):
    kind: Literal[DeclarationKind.TYPEALIAS] = DeclarationKind.TYPEALIAS
    alias_type: TypeAnalysis | None


class ClassBase(BaseModel):
    bases: tuple[TypeAnalysis, ...]
    methods: tuple[MethodAnalysis, ...]
    variables: tuple[ClassVariableAnalysis, ...]
    type_aliases: tuple[ClassTypeAliasAnalysis, ...]

    inner_classes: tuple[InnerClassAnalysis, ...]


class ClassCommon(TypedDict):
    bases: tuple[TypeAnalysis, ...]
    methods: tuple[MethodAnalysis, ...]
    variables: tuple[ClassVariableAnalysis, ...]
    type_aliases: tuple[ClassTypeAliasAnalysis, ...]
    inner_classes: tuple[InnerClassAnalysis, ...]


class InnerClassAnalysis(MemberAnalysisBase, ClassBase):
    kind: Literal[DeclarationKind.CLASS] = DeclarationKind.CLASS


class ClassAnalysis(SymbolAnalysisBase, ClassBase):
    kind: Literal[DeclarationKind.CLASS] = DeclarationKind.CLASS
