from typing import Literal

from gyomu_schema.schemas.python.symbol_base import DeclarationKind, SymbolAnalysisBase
from gyomu_schema.schemas.python.type.type_analysis import TypeAnalysis


class TypeAliasAnalysis(SymbolAnalysisBase):
    """Represents the analysis of a type alias declaration."""

    kind: Literal[DeclarationKind.TYPEALIAS] = DeclarationKind.TYPEALIAS
    """The declaration kind, fixed to TYPEALIAS."""

    alias_type: TypeAnalysis | None
    """The underlying type analysis of the alias, if available."""
