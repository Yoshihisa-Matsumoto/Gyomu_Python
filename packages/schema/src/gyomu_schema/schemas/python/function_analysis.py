from typing import Literal

from gyomu_schema.schemas.python.callable import CallableAnalysisBase
from gyomu_schema.schemas.python.symbol_base import DeclarationKind, SymbolAnalysisBase


class FunctionAnalysis(SymbolAnalysisBase, CallableAnalysisBase):
    """Represents the analysis of a Python function."""

    kind: Literal[DeclarationKind.FUNCTION] = DeclarationKind.FUNCTION
    """The declaration kind, fixed to FUNCTION."""
