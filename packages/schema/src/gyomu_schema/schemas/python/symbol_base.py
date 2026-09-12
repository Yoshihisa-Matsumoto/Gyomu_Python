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
    VARIABLE = "variable"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    TYPEALIAS = "typealias"


class DeclarationAnalysisBase(BaseModel):
    name: str
    visibility: Visibility
    docstring: DocstringAnalysis | None
    decorators: tuple[DecoratorAnalysis, ...]
    identity: DeclarationIdentity


class SymbolAnalysisBase(DeclarationAnalysisBase):
    location: SourceLocation
    dependencies: tuple[DependencyAnalysis, ...]
    indent: int


class MemberAnalysisBase(DeclarationAnalysisBase):
    location: SourceLocation | None
    indent: int | None


class DeclarationCommon(TypedDict):
    name: str
    visibility: Visibility
    docstring: DocstringAnalysis | None
    decorators: tuple[DecoratorAnalysis, ...]


class SymbolCommon(DeclarationCommon):
    location: SourceLocation
    indent: int


class MemberCommon(DeclarationCommon):
    location: SourceLocation | None
    indent: int | None
