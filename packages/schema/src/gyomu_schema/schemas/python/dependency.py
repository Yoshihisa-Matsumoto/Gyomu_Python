from enum import StrEnum
from typing import Literal

from pydantic import BaseModel


class DependencyKind(StrEnum):
    IMPORT = "import"
    TYPE = "type"
    INHERITANCE = "inheritance"
    REFERENCE = "reference"


class LocalFileDependency(BaseModel):
    scope: Literal["local-file"]
    local_symbol_name: str


class ImportedSymbolDependency(BaseModel):
    scope: Literal["import"]
    local_symbol_name: str


class DependencyAnalysis(BaseModel):
    source: str
    target: LocalFileDependency | ImportedSymbolDependency
