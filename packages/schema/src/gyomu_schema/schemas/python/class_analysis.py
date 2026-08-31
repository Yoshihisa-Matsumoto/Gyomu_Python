from typing import Literal

from gyomu_schema.schemas.python.member_analysis import MemberAnalysisBase, MemberKind
from gyomu_schema.schemas.python.method_analysis import MethodAnalysis
from gyomu_schema.schemas.python.pydantic import PydanticModelAnalysis
from gyomu_schema.schemas.python.symbol_base import SymbolAnalysisBase, SymbolKind
from gyomu_schema.schemas.python.type import TypeAnalysis


class ClassVariableAnalysis(MemberAnalysisBase):
    kind: Literal[MemberKind.VARIABLE]

    type: TypeAnalysis | None
    value_source: str | None


class ClassAnalysis(SymbolAnalysisBase):
    kind: Literal[SymbolKind.CLASS]

    bases: tuple[TypeAnalysis, ...]
    methods: tuple[MethodAnalysis, ...]
    variables: tuple[ClassVariableAnalysis, ...]
    pydantic: PydanticModelAnalysis | None
