from enum import StrEnum
from typing import TypedDict

from pydantic import BaseModel

from gyomu_schema.schemas.python.decorator import DecoratorAnalysis
from gyomu_schema.schemas.python.dependency import DependencyAnalysis
from gyomu_schema.schemas.python.docstring import DocstringAnalysis
from gyomu_schema.schemas.python.location import SourceLocation
from gyomu_schema.schemas.python.types import DeclarationIdentity
from gyomu_schema.schemas.python.visibility import Visibility


class DeclarationKind(StrEnum):
    """Defines the kind of Python declaration."""

    VARIABLE = "variable"
    """Variable declaration kind."""

    CLASS = "class"
    """Class declaration kind."""

    FUNCTION = "function"
    """Function declaration kind."""

    METHOD = "method"
    """Method declaration kind."""

    TYPEALIAS = "typealias"
    """Type alias declaration kind."""


class DeclarationAnalysisBase(BaseModel):
    """Base model for declaration analysis containing common metadata fields."""

    name: str
    """Name of the declaration."""

    visibility: Visibility
    """Visibility level of the declaration."""

    docstring: DocstringAnalysis | None
    """Analyzed docstring associated with the declaration, if present."""

    decorators: tuple[DecoratorAnalysis, ...]
    """Decorators applied to the declaration."""

    identity: DeclarationIdentity
    """Unique identity of the declaration."""


class SymbolAnalysisBase(DeclarationAnalysisBase):
    """Base model for symbol analysis extending declaration analysis with location
    and dependency information.
    """

    location: SourceLocation
    """Source code location of the symbol."""

    dependencies: tuple[DependencyAnalysis, ...]
    """Dependencies referenced by the symbol."""

    indent: int
    """Indentation level of the symbol."""


class MemberAnalysisBase(DeclarationAnalysisBase):
    """Base model for member analysis extending declaration analysis with optional
    location and indentation.
    """

    location: SourceLocation | None
    """Source code location of the member, if available."""

    indent: int | None
    """Indentation level of the member, if available."""


class DeclarationCommon(TypedDict):
    """TypedDict representing common declaration fields."""

    name: str
    """Name of the declaration."""

    visibility: Visibility
    """Visibility level of the declaration."""

    docstring: DocstringAnalysis | None
    """Analyzed docstring associated with the declaration, if present."""

    decorators: tuple[DecoratorAnalysis, ...]
    """Decorators applied to the declaration."""


class SymbolCommon(DeclarationCommon):
    """TypedDict representing common symbol fields including location and
    indentation.
    """

    location: SourceLocation
    """Source code location of the symbol."""

    indent: int
    """Indentation level of the symbol."""


class MemberCommon(DeclarationCommon):
    """TypedDict representing common member fields with optional location and
    indentation.
    """

    location: SourceLocation | None
    """Source code location of the member, if available."""

    indent: int | None
    """Indentation level of the member, if available."""
