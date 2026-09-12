from typing import Literal

from gyomu_schema.schemas.python.callable import CallableAnalysisBase
from gyomu_schema.schemas.python.symbol_base import DeclarationKind, SymbolAnalysisBase


class FunctionAnalysis(SymbolAnalysisBase, CallableAnalysisBase):
    kind: Literal[DeclarationKind.FUNCTION] = DeclarationKind.FUNCTION
