from griffe import Decorator
from gyomu_infra.logger import logger
from gyomu_schema.schemas.python.decorator import DecoratorAnalysis, DecoratorArgument
from gyomu_schema.schemas.python.type.structure import (
    LiteralValue,
    NameStructureAnalysis,
)
from gyomu_schema.schemas.python.type.type_analysis import (
    AttributeStructureAnalysis,
    CallStructureAnalysis,
    ExpressionAnalysis,
    KeywordStructureAnalysis,
    TypeExpression,
)

from gyomu_python_analysis.analysis.analyzers.expression.expr import (
    analyze_type_expression,
)
from gyomu_python_analysis.analysis.analyzers.internal.location import (
    calculate_decorator_location,
)


def analyze_decorators(
    decorators: list[Decorator],
    source_lines: list[str],
) -> list[DecoratorAnalysis]:
    returns: list[DecoratorAnalysis] = []
    for dec in decorators:
        returns.append(analyze_decorator(dec, source_lines))

    return returns


def analyze_decorator(
    decorator: Decorator,
    source_lines: list[str],
) -> DecoratorAnalysis:
    value = analyze_type_expression(decorator.value)
    name: str
    arguments: list[DecoratorArgument] = []
    if isinstance(value, LiteralValue):
        name = str(value.value)

    else:
        name, arguments = _retrieve_expression_name(value)

    return DecoratorAnalysis(
        location=calculate_decorator_location(
            decorator=decorator, source_lines=source_lines
        ),
        name=name,
        arguments=tuple(arguments),
    )


def _retrieve_expression_name(
    expression: ExpressionAnalysis,
) -> tuple[str, list[DecoratorArgument]]:
    if isinstance(expression, NameStructureAnalysis):
        return expression.name, []
    elif isinstance(expression, AttributeStructureAnalysis):
        return ".".join(_retrieve_attribute_names(expression)), []
    elif isinstance(expression, CallStructureAnalysis):
        name, _ = _retrieve_expression_name(expression.function)
        arguments: list[DecoratorArgument] = []
        for arg in expression.arguments:
            arguments.append(_retrieve_expression_argument(arg))
        return name, arguments
    else:
        logger.error(f"Unsupported Expression: {expression.kind}")
        return "", []


def _retrieve_expression_argument(expression: TypeExpression) -> DecoratorArgument:
    if isinstance(expression, KeywordStructureAnalysis):
        return DecoratorArgument(expression=expression.value, name=expression.name)
    return DecoratorArgument(expression=expression)


def _retrieve_attribute_names(attribute: AttributeStructureAnalysis) -> list[str]:
    strings: list[str] = []
    for value in attribute.values:
        if isinstance(value, LiteralValue):
            strings.append(str(value.value))
        elif isinstance(value, NameStructureAnalysis):
            strings.append(value.name)
        elif isinstance(value, AttributeStructureAnalysis):
            for child in _retrieve_attribute_names(value):
                strings.append(child)
    return strings
