from typing import Literal

from gyomu_schema.schemas.python.symbol_base import SymbolAnalysisBase, SymbolKind
from gyomu_schema.schemas.python.type import TypeAnalysis


class VariableAnalysis(SymbolAnalysisBase):
    kind: Literal[SymbolKind.VARIABLE]

    type: TypeAnalysis | None
    value_source: str | None
