from griffe import Attribute
from gyomu_schema.schemas.python.symbol_base import SymbolKind
from gyomu_schema.schemas.python.variable import VariableAnalysis

from gyomu_python_analysis.analysis.analyzers.context import (
    MemberPath,
    SymbolContext,
    build_declaration_identity,
)
from gyomu_python_analysis.analysis.analyzers.internal.common import build_symbol_common
from gyomu_python_analysis.analysis.analyzers.types import analyze_type


def analyze_variable(
    variable: Attribute, name: str, source_lines: list[str], context: SymbolContext
) -> VariableAnalysis:
    member_path: MemberPath = ()
    variable_common = build_symbol_common(
        symbol=variable, name=name, source_lines=source_lines, context=context
    )
    type = analyze_type(variable.annotation, context)
    return VariableAnalysis(
        **variable_common,
        kind=SymbolKind.VARIABLE,
        dependencies=tuple(context.dependencies),
        type=type,
        value_source=str(variable.value) if variable.value is not None else None,
        identity=build_declaration_identity(context, member_path),
    )
