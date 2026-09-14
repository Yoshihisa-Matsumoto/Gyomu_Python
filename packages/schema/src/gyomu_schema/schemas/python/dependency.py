from dataclasses import dataclass
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel

from gyomu_schema.schemas.python.types import DeclarationIdentity, SymbolId


class DependencyKind(StrEnum):
    IMPORT = "import"
    TYPE = "type"
    INHERITANCE = "inheritance"
    REFERENCE = "reference"


class LocalFileDependency(BaseModel):
    scope: Literal["local-file"] = "local-file"
    symbol_id: SymbolId


class ImportedSymbolDependency(BaseModel):
    scope: Literal["import"] = "import"
    symbol_id: SymbolId


class DependencyAnalysis(BaseModel):
    source: DeclarationIdentity
    target: LocalFileDependency | ImportedSymbolDependency


@dataclass(frozen=True)
class DependencySummary:
    target: LocalFileDependency | ImportedSymbolDependency
