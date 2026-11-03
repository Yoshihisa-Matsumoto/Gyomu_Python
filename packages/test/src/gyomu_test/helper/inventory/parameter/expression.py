from gyomu_python_analysis.resolve.reference import (
    resolve_declaration_identity,
)
from gyomu_schema.schemas.config.test.model_defaults import (
    Argument,
    Arguments,
    AttributeParameter,
    CallParameter,
    DictEntry,
    DictParameter,
    KeywordArgument,
    LambdaParameter,
    ListParameter,
    LiteralParameter,
    NameParameter,
    NoneParameter,
    Parameter,
    TupleParameter,
)
from gyomu_schema.schemas.python.module import ModuleAnalysis
from gyomu_schema.schemas.python.type.expression import (
    ArgumentAnalysis,
    ArgumentsAnalysis,
    AttributeExpressionAnalysis,
    CallExpressionAnalysis,
    DictionaryExpressionAnalysis,
    ExpressionAnalysis,
    KeywordAnalysis,
    LambdaExpressionAnalysis,
    ListExpressionAnalysis,
    NameExpressionAnalysis,
    NoneExpressionAnalysis,
    TupleExpressionAnalysis,
)
from gyomu_schema.schemas.python.type.structure import (
    LiteralValue,
)


def build_parameter_from_expression(
    expression: ExpressionAnalysis, module: ModuleAnalysis
) -> Parameter:
    if isinstance(expression, LiteralValue):
        return LiteralParameter(value=expression.value)
    if isinstance(expression, NoneExpressionAnalysis):
        return NoneParameter()
    if isinstance(expression, NameExpressionAnalysis):
        return NameParameter(name=expression.name)
    if isinstance(expression, CallExpressionAnalysis):
        return _build_call_parameter(expression, module)
    if isinstance(expression, ListExpressionAnalysis):
        return _build_list_parameter(expression, module)
    if isinstance(expression, TupleExpressionAnalysis):
        return _build_tuple_parameter(expression, module)
    if isinstance(expression, DictionaryExpressionAnalysis):
        return _build_dict_parameter(expression, module)
    if isinstance(expression, AttributeExpressionAnalysis):
        return _build_attribute_parameter(expression, module)
    if isinstance(expression, LambdaExpressionAnalysis):
        return _build_lambda_parameter(expression, module)
    raise NotImplementedError(
        f"Unsupported parameter type: {type(expression).__name__}"
    )


def _build_argument(arg: ArgumentAnalysis, module: ModuleAnalysis) -> Argument:
    return Argument(
        arg=arg.arg,
        annotation=build_parameter_from_expression(
            expression=arg.annotation, module=module
        ),
    )


def _build_arguments(args: ArgumentsAnalysis, module: ModuleAnalysis) -> Arguments:

    return Arguments(
        posonlyargs=tuple(_build_argument(arg, module) for arg in args.posonlyargs),
        args=tuple(_build_argument(arg, module) for arg in args.args),
        vararg=_build_argument(args.vararg, module)
        if args.vararg is not None
        else None,
        kwonlyargs=tuple(_build_argument(arg, module) for arg in args.kwonlyargs),
        kw_defaults=tuple(
            build_parameter_from_expression(default, module)
            for default in args.kw_defaults
        ),
        kwarg=_build_argument(args.kwarg, module) if args.kwarg is not None else None,
        defaults=tuple(
            build_parameter_from_expression(default, module)
            for default in args.defaults
        ),
    )


def _build_lambda_parameter(
    expression: LambdaExpressionAnalysis, module: ModuleAnalysis
) -> LambdaParameter:
    body = build_parameter_from_expression(expression=expression.body, module=module)
    args = _build_arguments(expression.args, module)
    return LambdaParameter(body=body, args=args)


def _build_attribute_parameter(
    expression: AttributeExpressionAnalysis, module: ModuleAnalysis
) -> AttributeParameter:
    value_parameter = build_parameter_from_expression(
        expression=expression.value, module=module
    )

    return AttributeParameter(value=value_parameter, attribute=expression.attribute)


def _build_dict_parameter(
    expression: DictionaryExpressionAnalysis, module: ModuleAnalysis
) -> DictParameter:
    entries = tuple(
        DictEntry(
            key=build_parameter_from_expression(entry.key, module),
            value=build_parameter_from_expression(entry.value, module),
        )
        for entry in expression.entries
    )
    return DictParameter(entries=entries)


def _build_tuple_parameter(
    expression: TupleExpressionAnalysis, module: ModuleAnalysis
) -> TupleParameter:
    return TupleParameter(
        elements=tuple(
            build_parameter_from_expression(element, module)
            for element in expression.elements
        )
    )


def _build_list_parameter(
    array: ListExpressionAnalysis, module: ModuleAnalysis
) -> ListParameter:
    return ListParameter(
        elements=tuple(
            build_parameter_from_expression(element, module)
            for element in array.elements
        )
    )


def _build_kwarg(keyword: KeywordAnalysis, module: ModuleAnalysis) -> KeywordArgument:
    assert keyword.arg
    return KeywordArgument(
        name=keyword.arg,
        value=build_parameter_from_expression(expression=keyword.value, module=module),
    )


def _build_call_parameter(
    call: CallExpressionAnalysis, module: ModuleAnalysis
) -> CallParameter:
    assert isinstance(call.func, NameExpressionAnalysis)
    callable_identity = resolve_declaration_identity(
        reference_name=call.func.name, module=module
    )
    assert callable_identity is not None

    args = tuple(
        build_parameter_from_expression(expression=arg, module=module)
        for arg in call.args
    )
    kwargs = tuple(
        _build_kwarg(keyword=keyword, module=module) for keyword in call.keywords
    )

    return CallParameter(callable_identity=callable_identity, args=args, kwargs=kwargs)
