from pydantic import BaseModel

from gyomu_schema.schemas.python.docstring import DocstringAnalysis
from gyomu_schema.schemas.python.import_analysis import ImportAnalysis
from gyomu_schema.schemas.python.symbol import SymbolAnalysis
from gyomu_schema.schemas.python.types import PythonPath, SourceRelativePath


class ModuleAnalysis(BaseModel):
    """Defines the analysis results for a Python module, containing path, name, module
    name, docstring analysis, imports, and symbols.
    """

    path: SourceRelativePath
    """Source relative path of the module."""

    name: str
    """Name of the module."""

    module_name: PythonPath
    """Python module path."""

    docstring: DocstringAnalysis | None
    """Docstring analysis of the module, if present."""

    imports: tuple[ImportAnalysis, ...]
    """Tuple of import analyses in the module."""

    symbols: tuple[SymbolAnalysis, ...]
    """Tuple of symbol analyses defined in the module."""
