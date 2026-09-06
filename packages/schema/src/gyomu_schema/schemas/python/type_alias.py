from typing import Literal

from gyomu_schema.schemas.python.symbol_base import SymbolAnalysisBase, SymbolKind
from gyomu_schema.schemas.python.type.type_analysis import TypeAnalysis


class TypeAliasAnalysis(SymbolAnalysisBase):
    kind: Literal[SymbolKind.TYPEALIAS]

    alias_type: TypeAnalysis | None
