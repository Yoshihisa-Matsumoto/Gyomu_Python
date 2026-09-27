from griffe import Decorator
from gyomu_infra.logger import logger
from gyomu_schema.option.analysis import AnalysisOption
from gyomu_schema.schemas.python.decorator import DecoratorAnalysis, DecoratorArgument
from gyomu_schema.schemas.python.type.structure import (
    LiteralValue,
    NameStructureAnalysis,
)
from gyomu_schema.schemas.python.type.type_analysis import (
    AttributeStructureAnalysis,
    CallStructureAnalysis,
    KeywordStructureAnalysis,
    StructureAnalysis,
    TypeExpression,
)

from gyomu_python_analysis.analysis.analyzers.context import SymbolContext
from gyomu_python_analysis.analysis.analyzers.expression.expr import (
    analyze_type_expression,
)
from gyomu_python_analysis.analysis.analyzers.internal.location import (
    calculate_decorator_location,
)


def analyze_decorators(
    decorators: list[Decorator],
    context: SymbolContext,
    option: AnalysisOption | None,
) -> list[DecoratorAnalysis]:
    """Analyze a list of decorators.

    Analyzes a list of decorators.

    Args:
        decorators (list[Decorator]): List of decorators to analyze
        context (SymbolContext): Symbol context for analysis
        option (AnalysisOption | None): Analysis options

    Returns:
        list[DecoratorAnalysis]: List of decorator analyses
    """
    returns: list[DecoratorAnalysis] = []
    for dec in decorators:
        returns.append(analyze_decorator(dec, context, option))

    return returns


def analyze_decorator(
    decorator: Decorator,
    context: SymbolContext,
    option: AnalysisOption | None,
) -> DecoratorAnalysis:
    """Analyze an individual decorator.

    Analyzes an individual decorator.

    Args:
        decorator (Decorator): Decorator to analyze
        context (SymbolContext): Symbol context for analysis
        option (AnalysisOption | None): Analysis options

    Returns:
        DecoratorAnalysis: Decorator analysis result
    """
    value = analyze_type_expression(decorator.value, context, option)
    name: str
    arguments: list[DecoratorArgument] = []
    if isinstance(value, LiteralValue):
        name = str(value.value)

    else:
        name, arguments = _retrieve_expression_name(value)

    return DecoratorAnalysis(
        location=calculate_decorator_location(decorator=decorator, context=context),
        name=name,
        arguments=tuple(arguments),
    )


def _retrieve_expression_name(
    structure: StructureAnalysis,
) -> tuple[str, list[DecoratorArgument]]:
    """Retrieve expression name and arguments.

    Retrieves the expression name and arguments from a structure analysis.

    Args:
        structure (StructureAnalysis): Structure analysis to inspect

    Returns:
        tuple[str, list[DecoratorArgument]]: Tuple containing the expression name and a
            list of decorator arguments
    """
    if isinstance(structure, NameStructureAnalysis):
        return structure.name, []
    elif isinstance(structure, AttributeStructureAnalysis):
        return ".".join(_retrieve_attribute_names(structure)), []
    elif isinstance(structure, CallStructureAnalysis):
        name, _ = _retrieve_expression_name(structure.function)
        arguments: list[DecoratorArgument] = []
        for arg in structure.arguments:
            arguments.append(_retrieve_expression_argument(arg))
        return name, arguments
    else:
        logger.error(f"Unsupported Expression: {structure.kind}")
        return "", []


def _retrieve_expression_argument(expression: TypeExpression) -> DecoratorArgument:
    """Retrieve expression argument.

    Retrieves a decorator argument from an expression.

    Args:
        expression (TypeExpression): Expression to convert into a decorator argument

    Returns:
        DecoratorArgument: Decorator argument representation
    """
    if isinstance(expression, KeywordStructureAnalysis):
        return DecoratorArgument(expression=expression.value, name=expression.name)
    return DecoratorArgument(expression=expression)


def _retrieve_attribute_names(attribute: AttributeStructureAnalysis) -> list[str]:
    """Retrieve attribute names.

    Retrieves attribute names recursively from an attribute structure analysis.

    Args:
        attribute (AttributeStructureAnalysis): Attribute structure analysis to inspect

    Returns:
        list[str]: List of attribute name strings
    """
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
