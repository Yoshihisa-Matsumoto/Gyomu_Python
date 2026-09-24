from __future__ import annotations

from collections.abc import Sequence
from typing import Literal

from pydantic import BaseModel

# from gyomu_schema.schemas.python.type.generics import GenericsParameter
from gyomu_schema.schemas.python.type.structure import (
    EllipsisStructureAnalysis,
    LiteralValue,
    NameStructureAnalysis,
    NoneStructureAnalysis,
    TypeStructureKind,
    UnknownStructureAnalysis,
)


class TypeAnalysis(BaseModel):
    """Represents the analysis of a type, containing its text representation and
    optional structure analysis.
    """

    text: str
    """The text representation of the type."""

    structure: StructureAnalysis | None = None
    """The optional detailed structure analysis of the type."""


class UnionStructureAnalysis(BaseModel):
    """Represents the structure analysis of a union type expression."""

    kind: Literal[TypeStructureKind.UNION] = TypeStructureKind.UNION
    """The kind of the type structure, fixed as UNION."""

    types: tuple[TypeExpression, ...]
    """The constituent type expressions forming the union."""


class AttributeStructureAnalysis(BaseModel):
    """Represents the structure analysis of an attribute access or attribute type
    expression.
    """

    kind: TypeStructureKind = TypeStructureKind.ATTRIBUTE
    """The kind of the type structure, defaulting to ATTRIBUTE."""

    values: tuple[TypeExpression, ...]
    """The underlying type expressions involved in the attribute structure."""


class TupleStructureAnalysis(BaseModel):
    """Represents the structure analysis of a tuple type expression."""

    kind: TypeStructureKind = TypeStructureKind.TUPLE
    """The kind of the type structure, defaulting to TUPLE."""

    elements: Sequence[TypeExpression]
    """The element type expressions contained within the tuple."""

    variable_length: bool = False
    """Indicates whether the tuple is of variable length."""


class SetStructureAnalysis(BaseModel):
    """Represents the structure analysis of a set type expression."""

    kind: TypeStructureKind = TypeStructureKind.SET
    """The kind of the type structure, defaulting to SET."""

    element_type: TypeExpression
    """The type expression of the elements contained in the set."""


class LiteralStructureAnalysis(BaseModel):
    """Represents the structure analysis of a literal type expression."""

    kind: TypeStructureKind = TypeStructureKind.LITERAL
    """The kind of the type structure, defaulting to LITERAL."""

    value: TypeExpression
    """The literal value expression."""


class ArrayStructureAnalysis(BaseModel):
    """Represents the structure analysis of an array type expression."""

    kind: TypeStructureKind = TypeStructureKind.ARRAY
    """The kind of the type structure, defaulting to ARRAY."""

    element: TypeExpression
    """The type expression of the array element."""


class DictionaryStructureAnalysis(BaseModel):
    """Represents the structure analysis of a dictionary type expression."""

    kind: TypeStructureKind = TypeStructureKind.DICTIONARY
    """The kind of the type structure, defaulting to DICTIONARY."""

    keys: TypeExpression | None
    """The optional type expression for dictionary keys."""

    values: TypeExpression | None
    """The optional type expression for dictionary values."""


class CallableStructureAnalysis(BaseModel):
    """Represents the structure analysis of a callable type expression."""

    kind: TypeStructureKind = TypeStructureKind.CALLABLE
    """The kind of the type structure, defaulting to CALLABLE."""

    parameters: tuple[TypeExpression, ...] | None
    """The optional sequence of parameter type expressions for the callable."""

    return_type: TypeExpression
    """The return type expression of the callable."""


class CallStructureAnalysis(BaseModel):
    """Represents the structure analysis of a call expression."""

    kind: TypeStructureKind = TypeStructureKind.CALL
    """The kind of the type structure, defaulting to CALL."""

    function: StructureAnalysis
    """The structure analysis of the function being called."""

    arguments: tuple[TypeExpression, ...]
    """The arguments passed to the call expression."""


class GenericsStructureAnalysis(BaseModel):
    """Represents the structure analysis of a generic type expression."""

    kind: TypeStructureKind = TypeStructureKind.GENERIC
    """The kind of the type structure, defaulting to GENERIC."""

    base: TypeExpression
    """The base type expression being parameterized."""

    parameters: tuple[TypeExpression, ...]
    """The generic type parameter expressions."""


class KeywordStructureAnalysis(BaseModel):
    """Represents the structure analysis of a keyword argument or keyword type
    expression.
    """

    kind: TypeStructureKind = TypeStructureKind.KEYWORD
    """The kind of the type structure, defaulting to KEYWORD."""

    name: str
    """The name associated with the keyword."""

    value: TypeExpression
    """The type expression of the keyword value."""


type StructureAnalysis = (
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
    | KeywordStructureAnalysis
    | CallStructureAnalysis
    | EllipsisStructureAnalysis
)
"""A union type representing various forms of structure analysis for types."""


type TypeExpression = LiteralValue | StructureAnalysis
"""Represents a type expression as either a literal value or a structure analysis."""
