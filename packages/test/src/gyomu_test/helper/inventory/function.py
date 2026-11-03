import json

from gyomu_python_analysis.resolve.type_dump import dump_type
from gyomu_schema.schemas.config.test.model_defaults import (
    Argument,
    Arguments,
    AttributeParameter,
    CallParameter,
    DictParameter,
    LambdaParameter,
    ListParameter,
    LiteralParameter,
    NameParameter,
    NoneParameter,
    Parameter,
    TupleParameter,
)
from gyomu_schema.schemas.python.location import SourceLocation
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
            f"    {parameter.name}: {dump_type(parameter.parameter_type, return_type)}"
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
