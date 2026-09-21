from griffe import TypeAlias
from gyomu_schema.option.analysis import AnalysisOption
from gyomu_schema.schemas.python.type_alias import TypeAliasAnalysis

from gyomu_python_analysis.analysis.analyzers.context import (
    MemberPath,
    SymbolContext,
    build_declaration_identity,
)
from gyomu_python_analysis.analysis.analyzers.internal.common import build_symbol_common
from gyomu_python_analysis.analysis.analyzers.types import analyze_type


def analyze_type_alias(
    alias: TypeAlias,
    name: str,
    context: SymbolContext,
    option: AnalysisOption | None = None,
) -> TypeAliasAnalysis:
    member_path: MemberPath = ()
    alias_common = build_symbol_common(
        symbol=alias, name=name, context=context, option=option
    )
    type = analyze_type(alias.value, context, option)
    return TypeAliasAnalysis(
        **alias_common,
        dependencies=tuple(),
        alias_type=type,
        identity=build_declaration_identity(context, member_path),
    )
