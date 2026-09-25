from typing import Literal

from gyomu_schema.schemas.python.pydantic import PydanticFieldAnalysis
from gyomu_schema.schemas.python.symbol_base import DeclarationKind, SymbolAnalysisBase
from gyomu_schema.schemas.python.type.type_analysis import TypeAnalysis, TypeExpression


class VariableAnalysis(SymbolAnalysisBase):
    """Represents the analysis results for a Python variable."""

    kind: Literal[DeclarationKind.VARIABLE] = DeclarationKind.VARIABLE
    """The declaration kind, fixed to VARIABLE."""

    type: TypeAnalysis | None
    """The type analysis of the variable, if available."""

    value_source: str | None
    """The source representation of the variable's value."""

    value_expression: TypeExpression | None
    """The expression analysis of the variable's value, if available."""

    pydantic: PydanticFieldAnalysis | None
    """Pydantic-specific field analysis, if applicable."""
