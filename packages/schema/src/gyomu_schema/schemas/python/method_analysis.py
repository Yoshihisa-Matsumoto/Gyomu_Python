from typing import Literal

from gyomu_schema.schemas.python.callable import CallableAnalysisBase
from gyomu_schema.schemas.python.symbol_base import DeclarationKind, MemberAnalysisBase


class MethodAnalysis(MemberAnalysisBase, CallableAnalysisBase):
    kind: Literal[DeclarationKind.METHOD] = DeclarationKind.METHOD
