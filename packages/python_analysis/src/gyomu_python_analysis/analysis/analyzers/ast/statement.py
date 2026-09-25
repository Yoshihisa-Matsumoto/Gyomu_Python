import ast
from types import EllipsisType

from gyomu_infra.logger import logger
from gyomu_python_analysis.analysis.analyzers.context import SymbolContext
from gyomu_python_analysis.analysis.analyzers.dependency import register_dependency
from gyomu_schema.option.analysis import AnalysisOption
from gyomu_schema.schemas.python.type.expression import (
    AnnotationAssignStatementAnalysis,
    AssertStatementAnalysis,
    AssignStatementAnalysis,
    AttributeExpressionAnalysis,
    AwaitExpressionAnalysis,
    BinaryOperator,
    BinOpExpressionAnalysis,
    BoolOperator,
    BoolOpExpressionAnalysis,
    CallExpressionAnalysis,
    CompareExpressionAnalysis,
    ComparehensionAnalysis,
    CompareOperator,
    DictionaryCompareExpressionAnalysis,
    DictionaryEntryAnalysis,
    DictionaryExpressionAnalysis,
    EllipsisExpressionAnalysis,
    ExceptionStatementAnalysis,
    ExpressionAnalysis,
    ExpressionStatementAnalysis,
    FormattedConversion,
    FormattedValueExpressionAnalysis,
    IfStatementAnalysis,
    JoinedStrExpressionAnalysis,
    KeywordAnalysis,
    ListCompareExpressionAnalysis,
    ListExpressionAnalysis,
    NameExpressionAnalysis,
    NoneExpressionAnalysis,
    RaiseStatementAnalysis,
    ReturnStatementAnalysis,
    StarredExpressionAnalysis,
    StatementAnalysis,
    SubscriptExpressionAnalysis,
    TryStatementAnalysis,
    TupleExpressionAnalysis,
    UnaryOperator,
    UnaryOpExpressionAnalysis,
    UnknownExpressionAnalysis,
    UnknownStatementAnalysis,
    WhileStatementAnalysis,
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
    if isinstance(statement, ast.While):
        return _analyze_while(statement, context, option, need_registration_dependency)
    if isinstance(statement, ast.If):
        return _analyze_if(statement, context, option, need_registration_dependency)
    if isinstance(statement, ast.Try):
        return _analyze_try(statement, context, option, need_registration_dependency)
    if isinstance(statement, ast.Assert):
        return _analyze_assert(statement, context, option, need_registration_dependency)
    if isinstance(statement, ast.Raise):
        return _analyze_raise(statement, context, option, need_registration_dependency)
    if isinstance(statement, ast.AnnAssign):
        return _analyze_annotation_assign(
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
        return _analyze_call(expr, context, option, need_registration_dependency)
    if isinstance(expr, ast.Attribute):
        return _analyze_attribute(expr, context, option, need_registration_dependency)
    if isinstance(expr, ast.JoinedStr):
        return _analyze_joinedstr(expr, context, option, need_registration_dependency)
    if isinstance(expr, ast.Tuple):
        return analyze_tuple(expr, context, option, need_registration_dependency)
    if isinstance(expr, ast.BinOp):
        return _analyze_binop(expr, context, option, need_registration_dependency)
    if isinstance(expr, ast.BoolOp):
        return _analyze_boolop(expr, context, option, need_registration_dependency)
    if isinstance(expr, ast.FormattedValue):
        return _analyze_formatted_value(
            expr, context, option, need_registration_dependency
        )
    if isinstance(expr, ast.Compare):
        return _analyze_compare(expr, context, option, need_registration_dependency)
    if isinstance(expr, ast.Await):
        return _analyze_await(expr, context, option, need_registration_dependency)
    if isinstance(expr, ast.Subscript):
        return _analyze_subscript(expr, context, option, need_registration_dependency)
    if isinstance(expr, ast.DictComp):
        return _analyze_dict_compare(
            expr, context, option, need_registration_dependency
        )
    if isinstance(expr, ast.ListComp):
        return _analyze_list_compare(
            expr, context, option, need_registration_dependency
        )
    if isinstance(expr, ast.UnaryOp):
        return _analyze_unaryop(expr, context, option, need_registration_dependency)
    if isinstance(expr, ast.Starred):
        return _analyze_starred(expr, context, option, need_registration_dependency)
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


def _analyze_keyword(
    keyword: ast.keyword,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> KeywordAnalysis:
    return KeywordAnalysis(
        arg=keyword.arg,
        value=analyze_expression(
            keyword.value, context, option, need_registration_dependency
        ),
    )


def _analyze_comparehension(
    comprehension: ast.comprehension,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> ComparehensionAnalysis:
    return ComparehensionAnalysis(
        target=analyze_expression(
            comprehension.target, context, option, need_registration_dependency
        ),
        iter=analyze_expression(
            comprehension.iter, context, option, need_registration_dependency
        ),
        ifs=tuple(
            [
                analyze_expression(child, context, option, need_registration_dependency)
                for child in comprehension.ifs
            ]
        ),
        is_async=comprehension.is_async == 1,
    )


def _analyze_list_compare(
    compare: ast.ListComp,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> ListCompareExpressionAnalysis:

    return ListCompareExpressionAnalysis(
        element=analyze_expression(
            compare.elt, context, option, need_registration_dependency
        ),
        generators=tuple(
            [
                _analyze_comparehension(
                    child, context, option, need_registration_dependency
                )
                for child in compare.generators
            ]
        ),
    )


def _analyze_dict_compare(
    compare: ast.DictComp,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> DictionaryCompareExpressionAnalysis:

    return DictionaryCompareExpressionAnalysis(
        key=analyze_expression(
            compare.key, context, option, need_registration_dependency
        ),
        value=analyze_expression(
            compare.value, context, option, need_registration_dependency
        ),
        generators=tuple(
            [
                _analyze_comparehension(
                    child, context, option, need_registration_dependency
                )
                for child in compare.generators
            ]
        ),
    )


def _convert_compare_operator(op: ast.cmpop) -> CompareOperator:
    match op:
        case ast.Eq():
            return CompareOperator.EQ
        case ast.NotEq():
            return CompareOperator.NOT_EQ
        case ast.Lt():
            return CompareOperator.LT
        case ast.LtE():
            return CompareOperator.LT_E
        case ast.Gt():
            return CompareOperator.GT
        case ast.GtE():
            return CompareOperator.GT_E
        case ast.Is():
            return CompareOperator.IS
        case ast.IsNot():
            return CompareOperator.IS_NOT
        case ast.In():
            return CompareOperator.IN
        case ast.NotIn():
            return CompareOperator.NOT_IN
        case _:
            raise ValueError(f"Unsupported comparison operator: {type(op).__name__}")


def _analyze_compare(
    compare: ast.Compare,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> CompareExpressionAnalysis:

    return CompareExpressionAnalysis(
        left=analyze_expression(
            compare.left, context, option, need_registration_dependency
        ),
        ops=tuple([_convert_compare_operator(child) for child in compare.ops]),
        comparators=tuple(
            [
                analyze_expression(child, context, option, need_registration_dependency)
                for child in compare.comparators
            ]
        ),
    )


def _analyze_await(
    expression: ast.Await,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> AwaitExpressionAnalysis:

    return AwaitExpressionAnalysis(
        value=analyze_expression(
            expression.value, context, option, need_registration_dependency
        ),
    )


def _convert_formatted_value_conversion(conversion: int) -> FormattedConversion:
    match conversion:
        case 115:
            return FormattedConversion.STR
        case 114:
            return FormattedConversion.REPR
        case 97:
            return FormattedConversion.ASCII
        case -1:
            return FormattedConversion.NONE
        case _:
            raise ValueError(f"Unsupported formatted value conversion: {conversion}")


def _analyze_formatted_value(
    formatted_value: ast.FormattedValue,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> FormattedValueExpressionAnalysis:

    return FormattedValueExpressionAnalysis(
        value=analyze_expression(
            formatted_value.value, context, option, need_registration_dependency
        ),
        conversion=_convert_formatted_value_conversion(formatted_value.conversion),
        format_spec=analyze_expression(
            formatted_value.format_spec, context, option, need_registration_dependency
        ),
    )


def _analyze_subscript(
    subscript: ast.Subscript,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> SubscriptExpressionAnalysis:

    return SubscriptExpressionAnalysis(
        value=analyze_expression(
            subscript.value, context, option, need_registration_dependency
        ),
        slice=analyze_expression(
            subscript.slice, context, option, need_registration_dependency
        ),
    )


def _analyze_unaryop(
    unaryop: ast.UnaryOp,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> UnaryOpExpressionAnalysis:

    return UnaryOpExpressionAnalysis(
        operand=analyze_expression(
            unaryop.operand, context, option, need_registration_dependency
        ),
        op=_convert_unary_operator(unaryop.op),
    )


def _analyze_boolop(
    boolop: ast.BoolOp,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> BoolOpExpressionAnalysis:

    return BoolOpExpressionAnalysis(
        values=tuple(
            [
                analyze_expression(child, context, option, need_registration_dependency)
                for child in boolop.values
            ]
        ),
        op=_convert_boolop_operator(boolop.op),
    )


def _analyze_binop(
    binop: ast.BinOp,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> BinOpExpressionAnalysis:

    return BinOpExpressionAnalysis(
        left=analyze_expression(
            binop.left, context, option, need_registration_dependency
        ),
        right=analyze_expression(
            binop.right, context, option, need_registration_dependency
        ),
        op=_convert_binop_operator(binop.op),
    )


def _convert_unary_operator(op: ast.unaryop) -> UnaryOperator:
    match op:
        case ast.Invert():
            return UnaryOperator.INVERT
        case ast.Not():
            return UnaryOperator.NOT
        case ast.UAdd():
            return UnaryOperator.U_ADD
        case ast.USub():
            return UnaryOperator.U_SUB
        case _:
            raise ValueError(f"Unsupported unary operator: {type(op).__name__}")


def _convert_boolop_operator(op: ast.boolop) -> BoolOperator:
    match op:
        case ast.And():
            return BoolOperator.AND
        case ast.Or():
            return BoolOperator.OR
        case _:
            raise ValueError(f"Unsupported bool operator: {type(op).__name__}")


def _convert_binop_operator(op: ast.operator) -> BinaryOperator:
    match op:
        case ast.Add():
            return BinaryOperator.ADD
        case ast.Sub():
            return BinaryOperator.SUB
        case ast.Mult():
            return BinaryOperator.MULT
        case ast.MatMult():
            return BinaryOperator.MAT_MULT
        case ast.Div():
            return BinaryOperator.DIV
        case ast.Mod():
            return BinaryOperator.MOD
        case ast.Pow():
            return BinaryOperator.POW
        case ast.LShift():
            return BinaryOperator.L_SHIFT
        case ast.RShift():
            return BinaryOperator.R_SHIFT
        case ast.BitOr():
            return BinaryOperator.BIT_OR
        case ast.BitXor():
            return BinaryOperator.BIT_XOR
        case ast.BitAnd():
            return BinaryOperator.BIT_AND
        case ast.FloorDiv():
            return BinaryOperator.FLOOR_DIV
        case _:
            raise ValueError(f"Unsupported binary operator: {type(op).__name__}")


def _analyze_joinedstr(
    joinedstr: ast.JoinedStr,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> JoinedStrExpressionAnalysis:

    return JoinedStrExpressionAnalysis(
        values=tuple(
            [
                analyze_expression(child, context, option, need_registration_dependency)
                for child in joinedstr.values
            ]
        )
    )


def _analyze_attribute(
    attribute: ast.Attribute,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> AttributeExpressionAnalysis:

    return AttributeExpressionAnalysis(
        value=analyze_expression(
            attribute.value, context, option, need_registration_dependency
        ),
        attribute=attribute.attr,
    )


def _analyze_call(
    call: ast.Call,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> CallExpressionAnalysis:

    return CallExpressionAnalysis(
        func=analyze_expression(
            call.func, context, option, need_registration_dependency
        ),
        args=tuple(
            [
                analyze_expression(child, context, option, need_registration_dependency)
                for child in call.args
            ]
        ),
        keywords=tuple(
            [
                _analyze_keyword(child, context, option, need_registration_dependency)
                for child in call.keywords
            ]
        ),
    )


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


def _analyze_annotation_assign(
    statement: ast.AnnAssign,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> AnnotationAssignStatementAnalysis:
    return AnnotationAssignStatementAnalysis(
        target=analyze_expression(
            statement.target, context, option, need_registration_dependency
        ),
        annotation=analyze_expression(
            statement.annotation, context, option, need_registration_dependency
        ),
        value=analyze_expression(
            statement.value, context, option, need_registration_dependency
        ),
        simple=statement.simple == 1,
    )


def _analyze_raise(
    statement: ast.Raise,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> RaiseStatementAnalysis:
    return RaiseStatementAnalysis(
        exc=analyze_expression(
            statement.exc, context, option, need_registration_dependency
        ),
        cause=analyze_expression(
            statement.cause, context, option, need_registration_dependency
        ),
    )


def _analyze_assert(
    statement: ast.Assert,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> AssertStatementAnalysis:
    return AssertStatementAnalysis(
        test=analyze_expression(
            statement.test, context, option, need_registration_dependency
        ),
        message=analyze_expression(
            statement.msg, context, option, need_registration_dependency
        ),
    )


def _analyze_if(
    statement: ast.If,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> IfStatementAnalysis:
    return IfStatementAnalysis(
        test=analyze_expression(
            statement.test, context, option, need_registration_dependency
        ),
        body=tuple(
            [
                analyze_statement(child, context, option, need_registration_dependency)
                for child in statement.body
            ]
        ),
        orelse=tuple(
            [
                analyze_statement(child, context, option, need_registration_dependency)
                for child in statement.orelse
            ]
        ),
    )


def _analyze_while(
    statement: ast.While,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> WhileStatementAnalysis:
    return WhileStatementAnalysis(
        test=analyze_expression(
            statement.test, context, option, need_registration_dependency
        ),
        body=tuple(
            [
                analyze_statement(child, context, option, need_registration_dependency)
                for child in statement.body
            ]
        ),
        orelse=tuple(
            [
                analyze_statement(child, context, option, need_registration_dependency)
                for child in statement.orelse
            ]
        ),
    )


def _analyze_except_handler(
    statement: ast.ExceptHandler,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> ExceptionStatementAnalysis:
    return ExceptionStatementAnalysis(
        exception_type=analyze_expression(
            statement.type, context, option, need_registration_dependency
        ),
        name=statement.name,
        body=tuple(
            [
                analyze_statement(child, context, option, need_registration_dependency)
                for child in statement.body
            ]
        ),
    )


def _analyze_try(
    statement: ast.Try,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> TryStatementAnalysis:
    return TryStatementAnalysis(
        body=tuple(
            [
                analyze_statement(child, context, option, need_registration_dependency)
                for child in statement.body
            ]
        ),
        orelse=tuple(
            [
                analyze_statement(child, context, option, need_registration_dependency)
                for child in statement.orelse
            ]
        ),
        finalbody=tuple(
            [
                analyze_statement(child, context, option, need_registration_dependency)
                for child in statement.finalbody
            ]
        ),
        handlers=tuple(
            [
                _analyze_except_handler(
                    child, context, option, need_registration_dependency
                )
                for child in statement.handlers
            ]
        ),
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


def _analyze_starred(
    starred: ast.Starred,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> StarredExpressionAnalysis:

    return StarredExpressionAnalysis(
        value=analyze_expression(
            starred.value, context, option, need_registration_dependency
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


def analyze_tuple(
    expression: ast.Tuple,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> TupleExpressionAnalysis:
    elements: list[ExpressionAnalysis] = [
        analyze_expression(item, context, option, need_registration_dependency)
        for item in expression.elts
    ]

    return TupleExpressionAnalysis(elements=tuple(elements))


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
