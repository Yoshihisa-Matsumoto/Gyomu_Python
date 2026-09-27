import ast

from griffe import Function
from griffe import ParameterKind as GriffeParameterKind
from gyomu_schema.option.analysis import AnalysisOption
from gyomu_schema.schemas.python.function_analysis import FunctionAnalysis
from gyomu_schema.schemas.python.parameter import ParameterAnalysis, ParameterKind
from gyomu_schema.schemas.python.type.expression import (
    EllipsisExpressionAnalysis,
    ExpressionStatementAnalysis,
    PassStatementAnalysis,
    StatementAnalysis,
)

from gyomu_python_analysis.analysis.analyzers.ast.statement import analyze_statement
from gyomu_python_analysis.analysis.analyzers.context import (
    SymbolContext,
)
from gyomu_python_analysis.analysis.analyzers.internal.common import build_symbol_common
from gyomu_python_analysis.analysis.analyzers.types import analyze_type


def _get_function_parameter_kind(kind: GriffeParameterKind | None) -> ParameterKind:
    """Converts a Griffe parameter kind to a schema ParameterKind.

    Returns:
        ParameterKind: The corresponding schema ParameterKind.
    """
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


def check_ellipsis_only(statements: list[StatementAnalysis]) -> bool:
    """Checks whether the statements consist solely of an ellipsis or a pass statement.

    Returns:
        bool: True if the statements contain only an ellipsis or pass, false otherwise.
    """
    return (
        len(statements) == 1
        and isinstance(statements[0], ExpressionStatementAnalysis)
        and isinstance(statements[0].value, EllipsisExpressionAnalysis)
    ) or (len(statements) == 1 and isinstance(statements[0], PassStatementAnalysis))


def analyze_function(
    func: Function,
    name: str,
    context: SymbolContext,
    ast: ast.FunctionDef | ast.AsyncFunctionDef,
    option: AnalysisOption | None = None,
) -> FunctionAnalysis:
    """Analyzes a function definition and returns its detailed analysis structure.

    Returns:
        FunctionAnalysis: The analyzed function representation.
    """
    # for dec in func.decorators:
    #     print(dec.as_dict())
    parameters: list[ParameterAnalysis] = []
    for param in func.parameters:
        parameters.append(
            ParameterAnalysis(
                name=param.name,
                kind=_get_function_parameter_kind(param.kind),
                type=analyze_type(param.annotation, context, option),
                default=None,
            )
        )

    statements: list[StatementAnalysis] = [
        analyze_statement(statement, context, option, False) for statement in ast.body
    ]
    is_ellipsis_only = check_ellipsis_only(statements)

    # pprint(func.as_dict())
    func_common = build_symbol_common(
        symbol=func, name=name, context=context, option=option
    )
    return_type = analyze_type(func.returns, context, option)
    return FunctionAnalysis(
        **func_common,
        dependencies=tuple([]),
        parameters=tuple(parameters),
        is_async="async" in func.labels,
        return_type=return_type,
        identity=context.declaration,
        is_ellipsis_only=is_ellipsis_only,
        statements=tuple(statements),
    )
