from griffe import Function
from griffe import ParameterKind as GriffeParameterKind
from gyomu_schema.schemas.python.function_analysis import FunctionAnalysis
from gyomu_schema.schemas.python.parameter import ParameterAnalysis, ParameterKind
from gyomu_schema.schemas.python.symbol_base import SymbolKind

from gyomu_python_analysis.analysis.analyzers.context import (
    MemberPath,
    SymbolContext,
    build_declaration_identity,
)
from gyomu_python_analysis.analysis.analyzers.internal.common import build_symbol_common
from gyomu_python_analysis.analysis.analyzers.types import analyze_type


def _get_function_parameter_kind(kind: GriffeParameterKind | None) -> ParameterKind:
    match kind:
        case GriffeParameterKind.keyword_only:
            return ParameterKind.KEYWORD_ONLY
        case GriffeParameterKind.positional_only:
            return ParameterKind.POSITIONAL_ONLY
        case GriffeParameterKind.positional_or_keyword:
            return ParameterKind.POSITIONAL_OR_KEYWORD
        case GriffeParameterKind.var_keyword:
            return ParameterKind.VAR_KEYWORD
        case GriffeParameterKind.var_positional:
            return ParameterKind.VAR_POSITIONAL
    raise ValueError(f"Invalid Parameter Kind: {str(kind)}")


def analyze_function(
    func: Function, name: str, source_lines: list[str], context: SymbolContext
) -> FunctionAnalysis:
    member_path: MemberPath = ()
    for dec in func.decorators:
        print(dec.as_dict())
    parameters: list[ParameterAnalysis] = []
    for param in func.parameters:
        parameters.append(
            ParameterAnalysis(
                name=param.name,
                kind=_get_function_parameter_kind(param.kind),
                type=analyze_type(param.annotation, context),
                default=None,
            )
        )
    # pprint(func.as_dict())
    func_common = build_symbol_common(
        symbol=func, name=name, source_lines=source_lines, context=context
    )
    return_type = analyze_type(func.returns, context)
    return FunctionAnalysis(
        **func_common,
        kind=SymbolKind.FUNCTION,
        dependencies=tuple(context.dependencies),
        parameters=tuple(parameters),
        is_async="async" in func.labels,
        return_type=return_type,
        identity=build_declaration_identity(context, member_path),
    )
