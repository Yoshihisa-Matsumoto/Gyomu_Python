import ast
from types import EllipsisType

from gyomu_infra.logger import logger
from gyomu_python_analysis.analysis.analyzers.context import SymbolContext
from gyomu_python_analysis.analysis.analyzers.dependency import register_dependency
from gyomu_schema.option.analysis import AnalysisOption
from gyomu_schema.schemas.python.type.expression import (
    AssignStatementAnalysis,
    DictionaryEntryAnalysis,
    DictionaryExpressionAnalysis,
    EllipsisExpressionAnalysis,
    ExpressionAnalysis,
    ExpressionStatementAnalysis,
    ListExpressionAnalysis,
    NameExpressionAnalysis,
    NoneExpressionAnalysis,
    ReturnStatementAnalysis,
    StatementAnalysis,
    UnknownExpressionAnalysis,
    UnknownStatementAnalysis,
)
from gyomu_schema.schemas.python.type.structure import (
    LiteralValue,
)


def analyze_statement(
    statement: ast.stmt,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool = True,
) -> StatementAnalysis:
    if isinstance(statement, ast.Assign):
        return _analyze_assign(statement, context, option, need_registration_dependency)
    if isinstance(statement, ast.Return):
        return _analyze_return(statement, context, option, need_registration_dependency)
    if isinstance(statement, ast.Expr):
        return _analyze_expression(
            statement, context, option, need_registration_dependency
        )

    logger.debug(f"unsupported statement: {repr(statement)}")
    return UnknownStatementAnalysis()


def analyze_expression(
    expr: ast.expr | None,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> ExpressionAnalysis:
    if expr is None:
        return NoneExpressionAnalysis()
    if isinstance(expr, ast.Constant):
        return _analyze_const(expr, context, option)
    if isinstance(expr, ast.Name):
        return analyze_expression_name(
            expr, context, option, need_registration_dependency
        )
    if isinstance(expr, ast.List):
        return analyze_array(expr, context, option, need_registration_dependency)
    if isinstance(expr, ast.Dict):
        return analyze_dictionary(expr, context, option, need_registration_dependency)
    if isinstance(expr, ast.Call):
        pass

    logger.debug(f"unsupported expression: {repr(expr)}")
    return UnknownExpressionAnalysis()


def _analyze_const(
    const: ast.Constant,
    context: SymbolContext,
    option: AnalysisOption | None,
) -> LiteralValue | EllipsisExpressionAnalysis | NoneExpressionAnalysis:
    if isinstance(const.value, str | bytes | bool | int | float | complex):
        return LiteralValue(value=const.value)
    if isinstance(const.value, EllipsisType):
        return EllipsisExpressionAnalysis()

    return NoneExpressionAnalysis()


def _analyze_assign(
    assign: ast.Assign,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> AssignStatementAnalysis:
    targets: list[ExpressionAnalysis] = []
    for target in assign.targets:
        targets.append(
            analyze_expression(target, context, option, need_registration_dependency)
        )
    value = analyze_expression(
        assign.value, context, option, need_registration_dependency
    )
    return AssignStatementAnalysis(targets=tuple(targets), value=value)


def _analyze_return(
    expression: ast.Return,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> ReturnStatementAnalysis:
    return ReturnStatementAnalysis(
        value=analyze_expression(
            expression.value, context, option, need_registration_dependency
        )
    )


def _analyze_expression(
    expression: ast.Expr,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> ExpressionStatementAnalysis:
    return ExpressionStatementAnalysis(
        value=analyze_expression(
            expression.value, context, option, need_registration_dependency
        )
    )


def analyze_expression_name(
    expression: ast.Name,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> NameExpressionAnalysis | NoneExpressionAnalysis:

    if need_registration_dependency:
        register_dependency(context.declaration, expression.id, context)
    return NameExpressionAnalysis(
        name=expression.id,
    )


def analyze_array(
    expression: ast.List,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> ListExpressionAnalysis:
    elements: list[ExpressionAnalysis] = [
        analyze_expression(item, context, option, need_registration_dependency)
        for item in expression.elts
    ]

    return ListExpressionAnalysis(elements=tuple(elements))


def analyze_dictionary(
    expression: ast.Dict,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> DictionaryExpressionAnalysis:
    entries: list[DictionaryEntryAnalysis] = []
    for key, value in zip(expression.keys, expression.values, strict=False):
        entries.append(
            DictionaryEntryAnalysis(
                key=analyze_expression(
                    key, context, option, need_registration_dependency
                ),
                value=analyze_expression(
                    value, context, option, need_registration_dependency
                ),
            )
        )
    return DictionaryExpressionAnalysis(entries=tuple(entries))
