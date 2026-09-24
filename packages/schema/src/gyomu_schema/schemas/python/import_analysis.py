from enum import StrEnum

from pydantic import BaseModel


class ImportKind(StrEnum):
    """Enumeration representing the kind of import.

    Defines the kind of import, distinguishing between module-level and symbol-level
    imports.
    """

    MODULE = "module"
    """Represents a module import."""

    SYMBOL = "symbol"
    """Represents a symbol import."""


class ImportAnalysis(BaseModel):
    """Represents analysis of an import statement.

    Contains detailed information about an import statement, including its local name,
    imported name, and kind.
    """

    local_name: str
    """The local alias or name used in the code."""

    imported_name: str
    """The actual name being imported from the module."""

    kind: ImportKind
    """The kind of import (module or symbol)."""
