from typing import Literal

from gyomu_schema.schemas.python.callable import CallableAnalysisBase
from gyomu_schema.schemas.python.symbol_base import DeclarationKind, MemberAnalysisBase


class MethodAnalysis(MemberAnalysisBase, CallableAnalysisBase):
    """Represents analysis for a method declaration."""

    kind: Literal[DeclarationKind.METHOD] = DeclarationKind.METHOD
    """The declaration kind, fixed to method."""
