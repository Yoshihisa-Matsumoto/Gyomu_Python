from griffe import Attribute
from gyomu_python_analysis.analysis.analyzers.internal.common import build_symbol_common
from gyomu_schema.schemas.python.symbol_base import SymbolKind
from gyomu_schema.schemas.python.variable import VariableAnalysis


def analyze_variable(
    variable: Attribute,
    name: str,
    source_lines: list[str],
) -> VariableAnalysis:

    return VariableAnalysis(
        **build_symbol_common(
            symbol=variable,
            name=name,
            source_lines=source_lines,
        ),
        kind=SymbolKind.VARIABLE,
        docstring=None,
        decorators=tuple([]),
        dependencies=[],
        type=None,
        value_source=str(variable.value) if variable.value is not None else None,
    )
