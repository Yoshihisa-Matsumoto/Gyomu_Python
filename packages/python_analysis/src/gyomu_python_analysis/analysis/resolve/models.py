from dataclasses import dataclass

from gyomu_schema.schemas.python.import_analysis import ImportAnalysis
from gyomu_schema.schemas.python.types import PythonPath, SymbolId


@dataclass(frozen=True)
class ResolvedReference:
    import_analysis: ImportAnalysis | None
    module_path: PythonPath
    symbol_id: SymbolId | None
