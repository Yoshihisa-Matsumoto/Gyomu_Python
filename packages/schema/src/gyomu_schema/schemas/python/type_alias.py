from typing import Literal

from gyomu_schema.schemas.python.symbol_base import DeclarationKind, SymbolAnalysisBase
from gyomu_schema.schemas.python.type.type_analysis import TypeAnalysis


class TypeAliasAnalysis(SymbolAnalysisBase):
    kind: Literal[DeclarationKind.TYPEALIAS] = DeclarationKind.TYPEALIAS

    alias_type: TypeAnalysis | None
