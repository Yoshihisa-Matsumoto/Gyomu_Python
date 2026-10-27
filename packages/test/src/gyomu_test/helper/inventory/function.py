import json

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
from gyomu_schema.schemas.python.location import SourceLocation
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
from gyomu_schema.schemas.testing.helper import HelperFileInventory, HelperInventoryItem

from gyomu_test.helper.inventory.naming import _build_class_name_from_helper_name


def read_function_code(
    file_inventory: HelperFileInventory,
    location: SourceLocation,
) -> str:
    return "".join(
        file_inventory.source_lines[location.start_line - 1 : location.end_line]
    )


def _convert_to_code(parameter: Parameter) -> str:
    if isinstance(parameter, LiteralParameter):
        return _convert_literal_to_code(parameter.value)

    if isinstance(parameter, NoneParameter):
        return "None"
    if isinstance(parameter, AttributeParameter):
        return f"{_convert_to_code(parameter.value)}.{parameter.attribute}"
    if isinstance(parameter, TupleParameter):
        elements = ", ".join(
            _convert_to_code(element) for element in parameter.elements
        )
        if not parameter.elements:
            return "()"
        return f"({elements},)"
    if isinstance(parameter, ListParameter):
        elements = ", ".join(
            _convert_to_code(element) for element in parameter.elements
        )
        return f"[{elements}]"
    if isinstance(parameter, DictParameter):
        entries = ", ".join(
            f"{_convert_to_code(entry.key)}: {_convert_to_code(entry.value)}"
            for entry in parameter.entries
        )
        return f"{{{entries}}}"
    if isinstance(parameter, LambdaParameter):
        arguments = _convert_lambda_arguments(parameter.args)
        body = _convert_to_code(parameter.body)
        return f"lambda {arguments}: {body}"
    if isinstance(parameter, CallParameter):
        args = ", ".join(_convert_to_code(arg) for arg in parameter.args)
        kwargs = ", ".join(
            f"{kwarg.name} = {_convert_to_code(kwarg.value)}"
            for kwarg in parameter.kwargs
        )
        if args == "" and kwargs == "":
            args_str = ""
        elif args != "" and kwargs == "":
            args_str = args
        elif args == "" and kwargs != "":
            args_str = kwargs
        else:
            args_str = f"{args}, {kwargs}"
        return f"{parameter.callable_identity.get_symbol_name()}({args_str})"

    if isinstance(parameter, NameParameter):
        return parameter.name
    raise NotImplementedError(f"Unsupported parameter type: {type(parameter).__name__}")


def _convert_lambda_arguments(arguments: Arguments) -> str:
    parts: list[str] = []

    # Positional-only arguments
    parts.extend(_convert_argument(argument) for argument in arguments.posonlyargs)

    if arguments.posonlyargs:
        parts.append("/")

    # Regular arguments and positional defaults
    positional_arguments = [
        *arguments.posonlyargs,
        *arguments.args,
    ]
    positional_defaults = arguments.defaults

    default_start = len(positional_arguments) - len(positional_defaults)

    for index, argument in enumerate(arguments.args):
        default_index = index + len(arguments.posonlyargs) - default_start
        if default_index >= 0:
            parts.append(
                f"{argument.arg} = "
                f"{_convert_to_code(positional_defaults[default_index])}"
            )
        else:
            parts.append(argument.arg)

    # *args or a bare * for keyword-only arguments
    if arguments.vararg is not None:
        parts.append(f"*{arguments.vararg.arg}")
    elif arguments.kwonlyargs:
        parts.append("*")

    # Keyword-only arguments
    for argument, default in zip(
        arguments.kwonlyargs,
        arguments.kw_defaults,
        strict=True,
    ):
        if isinstance(default, NoneParameter):
            parts.append(argument.arg)
        else:
            parts.append(f"{argument.arg} = {_convert_to_code(default)}")

    # **kwargs
    if arguments.kwarg is not None:
        parts.append(f"**{arguments.kwarg.arg}")

    return ", ".join(parts)


def _convert_argument(argument: Argument) -> str:
    return argument.arg


#     return repr(value)
def _convert_literal_to_code(
    value: str | bytes | bool | int | float | complex | None,
) -> str:
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)

    return repr(value)


def _generate_function_parameter_default_code(default: Parameter | None) -> str:
    if default is None:
        return ""
    else:
        return f" = {_convert_to_code(default)}"


def generate_function_code(item: HelperInventoryItem) -> str:
    return_type = _build_class_name_from_helper_name(function_name=item.function_name)

    if not item.parameters:
        return (
            f"def {item.function_name}() -> {return_type}:\n"
            f"    return {return_type}()\n"
        )

    parameters = ",\n".join(
        (
            f"    {parameter.name}: {parameter.parameter_type.text}"
            f"{_generate_function_parameter_default_code(parameter.default)}"
        )
        for parameter in item.parameters
    )
    arguments = ",\n".join(
        f"        {parameter.name}={parameter.name}" for parameter in item.parameters
    )

    return (
        f"def {item.function_name}(\n"
        f"{parameters},\n"
        f") -> {return_type}:\n"
        f"    return {return_type}(\n"
        f"{arguments},\n"
        f"    )\n"
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
