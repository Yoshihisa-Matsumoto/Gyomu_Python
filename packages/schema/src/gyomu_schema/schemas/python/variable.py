from typing import Literal

from gyomu_schema.schemas.python.symbol_base import DeclarationKind, SymbolAnalysisBase
from gyomu_schema.schemas.python.type.type_analysis import TypeAnalysis


class VariableAnalysis(SymbolAnalysisBase):
    kind: Literal[DeclarationKind.VARIABLE] = DeclarationKind.VARIABLE

    type: TypeAnalysis | None
    value_source: str | None
