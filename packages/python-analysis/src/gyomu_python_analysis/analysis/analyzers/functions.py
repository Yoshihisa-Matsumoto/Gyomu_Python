from griffe import Function
from griffe import ParameterKind as GriffeParameterKind
from gyomu_python_analysis.analysis.analyzers.internal.common import build_symbol_common
from gyomu_schema.schemas.python.function_analysis import FunctionAnalysis
from gyomu_schema.schemas.python.parameter import ParameterAnalysis, ParameterKind
from gyomu_schema.schemas.python.symbol_base import SymbolKind


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
    func: Function,
    name: str,
    source_lines: list[str],
) -> FunctionAnalysis:
    parameters: list[ParameterAnalysis] = []
    for param in func.parameters:
        parameters.append(
            ParameterAnalysis(
                name=param.name,
                kind=_get_function_parameter_kind(param.kind),
                type=None,
                default=None,
            )
        )
    # pprint(func.as_dict())
    return FunctionAnalysis(
        **build_symbol_common(
            symbol=func,
            name=name,
            source_lines=source_lines,
        ),
        kind=SymbolKind.FUNCTION,
        docstring=None,
        decorators=tuple([]),
        dependencies=[],
        parameters=tuple(parameters),
        is_async="async" in func.labels,
        return_type=str(func.returns) if func.returns is not None else None,
    )
