from enum import StrEnum
from typing import Literal

from pydantic import BaseModel

from gyomu_schema.schemas.python.types import DeclarationIdentity, SymbolId


class DependencyKind(StrEnum):
    """Defines the kinds of dependencies that can exist between Python symbols."""

    IMPORT = "import"
    """Represents an import dependency."""

    TYPE = "type"
    """Represents a type dependency."""

    INHERITANCE = "inheritance"
    """Represents an inheritance dependency."""

    REFERENCE = "reference"
    """Represents a general reference dependency."""


class LocalFileDependency(BaseModel):
    """Defines a local file dependency containing a symbol ID."""

    scope: Literal["local-file"] = "local-file"
    """The scope of the dependency, fixed to local-file."""

    symbol_id: SymbolId
    """The target symbol identifier."""


class ImportedSymbolDependency(BaseModel):
    """Defines an imported symbol dependency containing a symbol ID."""

    scope: Literal["import"] = "import"
    """The scope of the dependency, fixed to import."""

    symbol_id: SymbolId
    """The target symbol identifier."""


class DependencyAnalysis(BaseModel):
    """Represents the analysis of a dependency between a source declaration and a
    target dependency.
    """

    source: DeclarationIdentity
    """The declaration identity of the source."""

    target: LocalFileDependency | ImportedSymbolDependency
    """The target dependency, which may be local or imported."""


class DependencySummary(BaseModel):
    """Represents a summary of a dependency target."""

    target: LocalFileDependency | ImportedSymbolDependency
    """The target dependency, which may be local or imported."""
