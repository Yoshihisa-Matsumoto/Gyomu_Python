from griffe import TypeAlias
from gyomu_schema.schemas.python.symbol_base import SymbolKind
from gyomu_schema.schemas.python.type_alias import TypeAliasAnalysis

from gyomu_python_analysis.analysis.analyzers.context import (
    MemberPath,
    SymbolContext,
    build_declaration_identity,
)
from gyomu_python_analysis.analysis.analyzers.internal.common import build_symbol_common
from gyomu_python_analysis.analysis.analyzers.types import analyze_type


def analyze_type_alias(
    alias: TypeAlias, name: str, context: SymbolContext
) -> TypeAliasAnalysis:
    member_path: MemberPath = ()
    alias_common = build_symbol_common(symbol=alias, name=name, context=context)
    type = analyze_type(alias.value, context)
    return TypeAliasAnalysis(
        **alias_common,
        kind=SymbolKind.TYPEALIAS,
        dependencies=tuple(),
        alias_type=type,
        identity=build_declaration_identity(context, member_path),
    )
