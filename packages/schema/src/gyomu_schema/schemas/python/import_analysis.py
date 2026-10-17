from enum import StrEnum

from pydantic import BaseModel

from gyomu_schema.schemas.python.types import PythonPath


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

    def get_module_path(self) -> PythonPath:
        if self.kind == ImportKind.MODULE:
            return PythonPath(self.imported_name)

        if "." not in self.imported_name:
            return PythonPath("")

        module_name, _ = self.imported_name.rsplit(".", maxsplit=1)
        return PythonPath(module_name)
