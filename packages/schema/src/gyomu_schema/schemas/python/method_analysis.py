from typing import Literal

from gyomu_schema.schemas.python.callable import CallableAnalysisBase
from gyomu_schema.schemas.python.member_analysis import MemberAnalysisBase, MemberKind


class MethodAnalysis(MemberAnalysisBase, CallableAnalysisBase):
    kind: Literal[MemberKind.METHOD]
