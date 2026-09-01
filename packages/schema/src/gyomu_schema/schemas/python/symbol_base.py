from enum import StrEnum
from typing import TypedDict

from pydantic import BaseModel

from gyomu_schema.schemas.python.decorator import DecoratorAnalysis
from gyomu_schema.schemas.python.dependency import DependencyAnalysis
from gyomu_schema.schemas.python.docstring import DocstringAnalysis
from gyomu_schema.schemas.python.location import SourceLocation
from gyomu_schema.schemas.python.visibility import Visibility


class SymbolKind(StrEnum):
    VARIABLE = "variable"
    CLASS = "class"
    FUNCTION = "function"


class SymbolAnalysisBase(BaseModel):
    name: str
    visibility: Visibility
    location: SourceLocation
    docstring: DocstringAnalysis | None
    decorators: tuple[DecoratorAnalysis, ...]
    dependencies: list[DependencyAnalysis]
    indent: int


class SymbolCommon(TypedDict):
    name: str
    location: SourceLocation
    visibility: Visibility
    indent: int
