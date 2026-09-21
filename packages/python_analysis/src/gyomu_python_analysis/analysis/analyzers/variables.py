from griffe import Attribute
from gyomu_schema.option.analysis import AnalysisOption
from gyomu_schema.schemas.python.pydantic import PydanticFieldAnalysis
from gyomu_schema.schemas.python.type.structure import LiteralValue
from gyomu_schema.schemas.python.type.type_analysis import (
    CallStructureAnalysis,
    TypeExpression,
)
from gyomu_schema.schemas.python.variable import VariableAnalysis

from gyomu_python_analysis.analysis.analyzers.context import (
    SymbolContext,
)
from gyomu_python_analysis.analysis.analyzers.expression.expr import (
    analyze_type_expression,
)
from gyomu_python_analysis.analysis.analyzers.internal.common import build_symbol_common
from gyomu_python_analysis.analysis.analyzers.pydantic import (
    analyze_pydantic,
    get_pydantic_field_from_annotated_type_expression,
)
from gyomu_python_analysis.analysis.analyzers.types import analyze_type


def analyze_variable(
    variable: Attribute,
    name: str,
    context: SymbolContext,
    option: AnalysisOption | None = None,
) -> VariableAnalysis:
    variable_common = build_symbol_common(
        symbol=variable, name=name, context=context, option=option
    )
    type = analyze_type(variable.annotation, context, option)

    value_expression = (
        analyze_type_expression(variable.value, context, option=option)
        if variable.value is not None
        else None
    )

    field_types: tuple[TypeExpression, CallStructureAnalysis] | None = (
        get_pydantic_field_from_annotated_type_expression(value_expression)
    )
    pydantic: PydanticFieldAnalysis | None = None
    if field_types is not None:
        assumed_type = field_types[0]
        target_type = field_types[1]
        if not isinstance(assumed_type, LiteralValue):
            pydantic = analyze_pydantic(assumed_type, target_type)

    return VariableAnalysis(
        **variable_common,
        dependencies=tuple(),
        type=type,
        value_source=str(variable.value) if variable.value is not None else None,
        identity=context.declaration,
        value_expression=value_expression,
        pydantic=pydantic,
    )
