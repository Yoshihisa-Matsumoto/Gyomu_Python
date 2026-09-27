import ast
from types import EllipsisType

from gyomu_infra.logger import logger
from gyomu_schema.option.analysis import AnalysisOption
from gyomu_schema.schemas.python.type.expression import (
    AnnotationAssignStatementAnalysis,
    ArgumentAnalysis,
    ArgumentsAnalysis,
    AssertStatementAnalysis,
    AssignStatementAnalysis,
    AttributeExpressionAnalysis,
    AugAssignStatementAnalysis,
    AwaitExpressionAnalysis,
    BinaryOperator,
    BinOpExpressionAnalysis,
    BoolOperator,
    BoolOpExpressionAnalysis,
    BreakStatementAnalysis,
    CallExpressionAnalysis,
    CompareExpressionAnalysis,
    ComparehensionAnalysis,
    CompareOperator,
    ComprehensionAnalysis,
    ContinueStatementAnalysis,
    DictionaryCompareExpressionAnalysis,
    DictionaryEntryAnalysis,
    DictionaryExpressionAnalysis,
    EllipsisExpressionAnalysis,
    ExceptionStatementAnalysis,
    ExpressionAnalysis,
    ExpressionStatementAnalysis,
    FormattedConversion,
    FormattedValueExpressionAnalysis,
    ForStatementAnalysis,
    FunctionDefStatementAnalysis,
    GeneratorExpressionAnalysis,
    GlobalStatementAnalysis,
    IfExpressionAnalysis,
    IfStatementAnalysis,
    JoinedStrExpressionAnalysis,
    KeywordAnalysis,
    LambdaExpressionAnalysis,
    ListCompareExpressionAnalysis,
    ListExpressionAnalysis,
    MatchAs,
    MatchCaseAnalysis,
    MatchClass,
    MatchMapping,
    MatchOr,
    MatchSequence,
    MatchSingleton,
    MatchStatementAnalysis,
    MatchValue,
    NamedExpressionAnalysis,
    NameExpressionAnalysis,
    NoneExpressionAnalysis,
    ParamSpecAnalysis,
    PassStatementAnalysis,
    PatternAnalysis,
    RaiseStatementAnalysis,
    ReturnStatementAnalysis,
    SetCompareExpressionAnalysis,
    SetExpressionAnalysis,
    SliceExpressionAnalysis,
    StarredExpressionAnalysis,
    StatementAnalysis,
    SubscriptExpressionAnalysis,
    TryStatementAnalysis,
    TupleExpressionAnalysis,
    TypeParameter,
    TypeVarAnalysis,
    TypeVarTupleAnalysis,
    UnaryOperator,
    UnaryOpExpressionAnalysis,
    UnknownExpressionAnalysis,
    UnknownStatementAnalysis,
    WhileStatementAnalysis,
    WithItemAnalysis,
    WithStatementAnalysis,
    YieldExpressionAnalysis,
    YieldFromExpressionAnalysis,
)
from gyomu_schema.schemas.python.type.structure import (
    LiteralValue,
)

from gyomu_python_analysis.analysis.analyzers.context import SymbolContext
from gyomu_python_analysis.analysis.analyzers.dependency import register_dependency


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
    if isinstance(statement, ast.For):
        return _analyze_for(statement, context, option, need_registration_dependency)
    if isinstance(statement, ast.With):
        return _analyze_with(statement, context, option, need_registration_dependency)
    if isinstance(statement, ast.Pass):
        return PassStatementAnalysis()
    if isinstance(statement, ast.Break):
        return BreakStatementAnalysis()
    if isinstance(statement, ast.Continue):
        return ContinueStatementAnalysis()
    if isinstance(statement, ast.AugAssign):
        return _analyze_augassign(
            statement, context, option, need_registration_dependency
        )
    if isinstance(statement, ast.Match):
        return _analyze_match(statement, context, option, need_registration_dependency)
    if isinstance(statement, ast.FunctionDef | ast.AsyncFunctionDef):
        return _analyze_function(
            statement, context, option, need_registration_dependency
        )
    if isinstance(statement, ast.Global):
        return _analyze_global(statement)

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
        return _analyze_const(expr, context, option, need_registration_dependency)
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
    if isinstance(expr, ast.Set):
        return analyze_set(expr, context, option, need_registration_dependency)
    if isinstance(expr, ast.SetComp):
        return _analyze_set_compare(expr, context, option, need_registration_dependency)
    if isinstance(expr, ast.Lambda):
        return _analyze_lambda(expr, context, option, need_registration_dependency)
    if isinstance(expr, ast.YieldFrom):
        return _analyze_yieldfrom(expr, context, option, need_registration_dependency)
    if isinstance(expr, ast.IfExp):
        return _analyze_ifexp(expr, context, option, need_registration_dependency)
    if isinstance(expr, ast.Yield):
        return _analyze_yield(expr, context, option, need_registration_dependency)
    if isinstance(expr, ast.GeneratorExp):
        return _analyze_generator_expression(
            expr, context, option, need_registration_dependency
        )
    if isinstance(expr, ast.Slice):
        return analyze_slice(expr, context, option, need_registration_dependency)
    if isinstance(expr, ast.NamedExpr):
        return _analyze_named(expr, context, option, need_registration_dependency)

    logger.debug(f"unsupported expression: {repr(expr)}")
    return UnknownExpressionAnalysis()


def _analyze_const(
    const: ast.Constant,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
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


def _analyze_set_compare(
    compare: ast.SetComp,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> SetCompareExpressionAnalysis:

    return SetCompareExpressionAnalysis(
        elt=analyze_expression(
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


def _analyze_argument(
    expression: ast.arg,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> ArgumentAnalysis:
    if expression is None:
        return None
    return ArgumentAnalysis(
        arg=expression.arg,
        type_comment=expression.type_comment,
        annotation=analyze_expression(
            expression.annotation, context, option, need_registration_dependency
        ),
    )


def _analyze_arguments(
    args: ast.arguments,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> ArgumentsAnalysis:
    return ArgumentsAnalysis(
        kw_defaults=tuple(
            [
                analyze_expression(child, context, option, need_registration_dependency)
                for child in args.kw_defaults
            ]
        ),
        defaults=tuple(
            [
                analyze_expression(child, context, option, need_registration_dependency)
                for child in args.defaults
            ]
        ),
        vararg=_analyze_argument(
            args.vararg, context, option, need_registration_dependency
        )
        if args.vararg is not None
        else None,
        kwarg=_analyze_argument(
            args.kwarg, context, option, need_registration_dependency
        )
        if args.kwarg is not None
        else None,
        posonlyargs=tuple(
            [
                _analyze_argument(child, context, option, need_registration_dependency)
                for child in args.posonlyargs
            ]
        ),
        args=tuple(
            [
                _analyze_argument(child, context, option, need_registration_dependency)
                for child in args.args
            ]
        ),
        kwonlyargs=tuple(
            [
                _analyze_argument(child, context, option, need_registration_dependency)
                for child in args.kwonlyargs
            ]
        ),
    )


def _analyze_lambda(
    expression: ast.Lambda,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> LambdaExpressionAnalysis:

    return LambdaExpressionAnalysis(
        args=_analyze_arguments(
            expression.args, context, option, need_registration_dependency
        ),
        body=analyze_expression(
            expression.body, context, option, need_registration_dependency
        ),
    )


def _analyze_comprehension(
    comprehension: ast.comprehension,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> ComprehensionAnalysis:
    """Analyze an AST comprehension node and return its structured representation."""

    return ComprehensionAnalysis(
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


def _analyze_generator_expression(
    generator: ast.GeneratorExp,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> GeneratorExpressionAnalysis:

    return GeneratorExpressionAnalysis(
        elt=analyze_expression(
            generator.elt, context, option, need_registration_dependency
        ),
        generators=tuple(
            [
                _analyze_comprehension(
                    child, context, option, need_registration_dependency
                )
                for child in generator.generators
            ]
        ),
    )


def _analyze_yield(
    unaryop: ast.Yield,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> YieldExpressionAnalysis:

    return YieldExpressionAnalysis(
        value=analyze_expression(
            unaryop.value, context, option, need_registration_dependency
        )
    )


def _analyze_yieldfrom(
    unaryop: ast.YieldFrom,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> YieldFromExpressionAnalysis:

    return YieldFromExpressionAnalysis(
        value=analyze_expression(
            unaryop.value, context, option, need_registration_dependency
        )
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


def _analyze_with_item(
    item: ast.withitem,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> WithItemAnalysis:
    return WithItemAnalysis(
        context_expr=analyze_expression(
            item.context_expr, context, option, need_registration_dependency
        ),
        optional_vars=analyze_expression(
            item.optional_vars, context, option, need_registration_dependency
        ),
    )


def _analyze_with(
    statement: ast.With,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> WithStatementAnalysis:

    return WithStatementAnalysis(
        body=tuple(
            [
                analyze_statement(child, context, option, need_registration_dependency)
                for child in statement.body
            ]
        ),
        items=tuple(
            [
                _analyze_with_item(child, context, option, need_registration_dependency)
                for child in statement.items
            ]
        ),
        type_comment=statement.type_comment,
    )


def _analyze_type_params(
    param: ast.type_param,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> TypeParameter:
    if isinstance(param, ast.TypeVar):
        return TypeVarAnalysis(
            name=param.name,
            bound=analyze_expression(
                param.bound, context, option, need_registration_dependency
            ),
            default_value=analyze_expression(
                param.default_value, context, option, need_registration_dependency
            ),
        )
    if isinstance(param, ast.ParamSpec):
        return ParamSpecAnalysis(
            name=param.name,
            default_value=analyze_expression(
                param.default_value, context, option, need_registration_dependency
            ),
        )
    if isinstance(param, ast.TypeVarTuple):
        return TypeVarTupleAnalysis(
            name=param.name,
            default_value=analyze_expression(
                param.default_value, context, option, need_registration_dependency
            ),
        )
    raise ValueError(f"Unsupported type parameter: {type(param).__name__}")


def _analyze_function(
    statement: ast.FunctionDef | ast.AsyncFunctionDef,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> FunctionDefStatementAnalysis:
    is_async = isinstance(statement, ast.AsyncFunctionDef)

    return FunctionDefStatementAnalysis(
        name=statement.name,
        is_async=is_async,
        args=_analyze_arguments(
            statement.args, context, option, need_registration_dependency
        ),
        body=tuple(
            [
                analyze_statement(child, context, option, need_registration_dependency)
                for child in statement.body
            ]
        ),
        decorator_list=tuple(
            [
                analyze_expression(child, context, option, need_registration_dependency)
                for child in statement.decorator_list
            ]
        ),
        returns=analyze_expression(
            statement.returns, context, option, need_registration_dependency
        ),
        type_comment=statement.type_comment,
        type_params=tuple(
            [
                _analyze_type_params(
                    child, context, option, need_registration_dependency
                )
                for child in statement.type_params
            ]
        ),
    )


def _analyze_pattern(
    pattern: ast.pattern,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> PatternAnalysis:
    if isinstance(pattern, ast.MatchValue):
        return MatchValue(
            value=analyze_expression(
                pattern.value, context, option, need_registration_dependency
            )
        )
    if isinstance(pattern, ast.MatchSingleton):
        return MatchSingleton(value=pattern.value)
    if isinstance(pattern, ast.MatchSequence):
        return MatchSequence(
            patterns=tuple(
                [
                    _analyze_pattern(
                        child, context, option, need_registration_dependency
                    )
                    for child in pattern.patterns
                ]
            ),
        )
    if isinstance(pattern, ast.MatchMapping):
        return MatchMapping(
            keys=tuple(
                [
                    analyze_expression(
                        child, context, option, need_registration_dependency
                    )
                    for child in pattern.keys
                ]
            ),
            patterns=tuple(
                [
                    _analyze_pattern(
                        child, context, option, need_registration_dependency
                    )
                    for child in pattern.patterns
                ]
            ),
            rest=pattern.rest,
        )

    if isinstance(pattern, ast.MatchClass):
        return MatchClass(
            cls=analyze_expression(
                pattern.cls, context, option, need_registration_dependency
            ),
            patterns=tuple(
                [
                    _analyze_pattern(
                        child, context, option, need_registration_dependency
                    )
                    for child in pattern.patterns
                ]
            ),
            kwd_patterns=tuple(
                [
                    _analyze_pattern(
                        child, context, option, need_registration_dependency
                    )
                    for child in pattern.kwd_patterns
                ]
            ),
            kwd_attrs=tuple(pattern.kwd_attrs),
        )
    if isinstance(pattern, ast.MatchAs):
        return MatchAs(
            pattern=_analyze_pattern(
                pattern.pattern, context, option, need_registration_dependency
            )
            if pattern.pattern is not None
            else None,
            name=pattern.name,
        )
    if isinstance(pattern, ast.MatchOr):
        return MatchOr(
            patterns=tuple(
                [
                    _analyze_pattern(
                        child, context, option, need_registration_dependency
                    )
                    for child in pattern.patterns
                ]
            ),
        )
    raise ValueError(f"Unsupported match case pattern: {type(pattern).__name__}")


def _analyze_matchcase(
    match_case: ast.match_case,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> MatchCaseAnalysis:
    return MatchCaseAnalysis(
        guard=analyze_expression(
            match_case.guard, context, option, need_registration_dependency
        ),
        body=tuple(
            [
                analyze_statement(child, context, option, need_registration_dependency)
                for child in match_case.body
            ]
        ),
        pattern=_analyze_pattern(
            match_case.pattern, context, option, need_registration_dependency
        ),
    )


def _analyze_match(
    statement: ast.Match,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> MatchStatementAnalysis:

    return MatchStatementAnalysis(
        cases=tuple(
            [
                _analyze_matchcase(child, context, option, need_registration_dependency)
                for child in statement.cases
            ]
        ),
        subject=analyze_expression(
            statement.subject, context, option, need_registration_dependency
        ),
    )


def _analyze_augassign(
    statement: ast.AugAssign,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> AugAssignStatementAnalysis:

    return AugAssignStatementAnalysis(
        target=analyze_expression(
            statement.target, context, option, need_registration_dependency
        ),
        op=_convert_binop_operator(statement.op),
        value=analyze_expression(
            statement.value, context, option, need_registration_dependency
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


def _analyze_global(
    statement: ast.Global,
) -> GlobalStatementAnalysis:
    return GlobalStatementAnalysis(names=tuple(statement.names))


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


def _analyze_ifexp(
    statement: ast.IfExp,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> IfExpressionAnalysis:
    return IfExpressionAnalysis(
        test=analyze_expression(
            statement.test, context, option, need_registration_dependency
        ),
        body=analyze_expression(
            statement.body, context, option, need_registration_dependency
        ),
        orelse=analyze_expression(
            statement.orelse, context, option, need_registration_dependency
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


def _analyze_for(
    statement: ast.For,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> ForStatementAnalysis:
    return ForStatementAnalysis(
        target=analyze_expression(
            statement.target, context, option, need_registration_dependency
        ),
        iter=analyze_expression(
            statement.iter, context, option, need_registration_dependency
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
        type_comment=statement.type_comment,
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


def _analyze_named(
    expression: ast.NamedExpr,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> NamedExpressionAnalysis:
    return NamedExpressionAnalysis(
        target=analyze_expression_name(
            expression.target, context, option, need_registration_dependency
        ),
        value=analyze_expression(
            expression.value, context, option, need_registration_dependency
        ),
    )


def analyze_expression_name(
    expression: ast.Name,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> NameExpressionAnalysis:

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


def analyze_slice(
    expression: ast.Slice,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> SliceExpressionAnalysis:

    return SliceExpressionAnalysis(
        lower=analyze_expression(
            expression.lower, context, option, need_registration_dependency
        ),
        upper=analyze_expression(
            expression.upper, context, option, need_registration_dependency
        ),
        step=analyze_expression(
            expression.step, context, option, need_registration_dependency
        ),
    )


def analyze_set(
    expression: ast.Set,
    context: SymbolContext,
    option: AnalysisOption | None,
    need_registration_dependency: bool,
) -> SetExpressionAnalysis:
    elements: list[ExpressionAnalysis] = [
        analyze_expression(item, context, option, need_registration_dependency)
        for item in expression.elts
    ]

    return SetExpressionAnalysis(elts=tuple(elements))


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
