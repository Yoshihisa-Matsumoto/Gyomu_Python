from griffe import Attribute
from gyomu_schema.schemas.python.symbol_base import SymbolKind
from gyomu_schema.schemas.python.variable import VariableAnalysis

from gyomu_python_analysis.analysis.analyzers.context import (
    SymbolContext,
)
from gyomu_python_analysis.analysis.analyzers.internal.common import build_symbol_common
from gyomu_python_analysis.analysis.analyzers.types import analyze_type


def analyze_variable(
    variable: Attribute, name: str, context: SymbolContext
) -> VariableAnalysis:
    variable_common = build_symbol_common(symbol=variable, name=name, context=context)
    type = analyze_type(variable.annotation, context)
    return VariableAnalysis(
        **variable_common,
        kind=SymbolKind.VARIABLE,
        dependencies=tuple(),
        type=type,
        value_source=str(variable.value) if variable.value is not None else None,
        identity=context.declaration,
    )
