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
    """Represents the analysis of a class variable."""

    kind: Literal[DeclarationKind.VARIABLE] = DeclarationKind.VARIABLE
    """The declaration kind."""

    type: TypeAnalysis | None
    """The type analysis of the variable."""

    value_source: str | None
    """The source of the variable value."""

    value_expression: TypeExpression | None
    """The value expression of the variable."""

    pydantic: PydanticFieldAnalysis | None
    """Pydantic-specific field analysis information."""


class ClassTypeAliasAnalysis(MemberAnalysisBase):
    """Represents the analysis of a class-level type alias."""

    kind: Literal[DeclarationKind.TYPEALIAS] = DeclarationKind.TYPEALIAS
    """The declaration kind."""

    alias_type: TypeAnalysis | None
    """The analysis of the aliased type."""


class ClassBase(BaseModel):
    """Base schema containing common structural elements of a class, such as bases,
    methods, variables, type aliases, and inner classes.
    """

    bases: tuple[TypeAnalysis, ...]
    """The base classes of the class."""

    methods: tuple[MethodAnalysis, ...]
    """The methods defined in the class."""

    variables: tuple[ClassVariableAnalysis, ...]
    """The variables defined in the class."""

    type_aliases: tuple[ClassTypeAliasAnalysis, ...]
    """The type aliases defined in the class."""

    inner_classes: tuple[InnerClassAnalysis, ...]
    """The inner classes defined within the class."""


class ClassCommon(TypedDict):
    """TypedDict representation of common class structural elements."""

    bases: tuple[TypeAnalysis, ...]
    """The base classes of the class."""

    methods: tuple[MethodAnalysis, ...]
    """The methods defined in the class."""

    variables: tuple[ClassVariableAnalysis, ...]
    """The variables defined in the class."""

    type_aliases: tuple[ClassTypeAliasAnalysis, ...]
    """The type aliases defined in the class."""

    inner_classes: tuple[InnerClassAnalysis, ...]
    """The inner classes defined within the class."""


class InnerClassAnalysis(MemberAnalysisBase, ClassBase):
    """Represents the analysis of an inner class."""

    kind: Literal[DeclarationKind.CLASS] = DeclarationKind.CLASS
    """The declaration kind."""


class ClassAnalysis(SymbolAnalysisBase, ClassBase):
    """Represents the complete analysis of a top-level class."""

    kind: Literal[DeclarationKind.CLASS] = DeclarationKind.CLASS
    """The declaration kind."""
