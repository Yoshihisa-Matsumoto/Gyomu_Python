from gyomu_schema.schemas.python.pydantic import PydanticFieldAnalysis
from gyomu_schema.schemas.python.type.expression import (
    CallExpressionAnalysis,
    ExpressionAnalysis,
    NameExpressionAnalysis,
    SubscriptExpressionAnalysis,
    TupleExpressionAnalysis,
)
from gyomu_schema.schemas.python.type.structure import (
    LiteralValue,
    NameStructureAnalysis,
    NoneStructureAnalysis,
)
from gyomu_schema.schemas.python.type.type_analysis import (
    GenericsStructureAnalysis,
    StructureAnalysis,
    TypeExpression,
    UnionStructureAnalysis,
)


def _is_field_required(field_type: StructureAnalysis | None) -> bool:
    """Determine whether a field is required based on its type analysis.

    Args:
        field_type (StructureAnalysis): The structure analysis of the field type.

    Returns:
        bool: True if the field is required, False otherwise.
    """
    if isinstance(field_type, NoneStructureAnalysis):
        return False
    if isinstance(field_type, UnionStructureAnalysis):
        for element in field_type.types:
            if isinstance(element, NoneStructureAnalysis):
                return False
    return True


def retrieve_str_value(value: ExpressionAnalysis) -> str | None:
    """Retrieve a string value from a type expression if it is a literal value.

    Args:
        value (TypeExpression): The type expression value to retrieve the string from.

    Returns:
        str | None: The string representation of the value, or None if not applicable.
    """
    if isinstance(value, LiteralValue):
        return str(value.value)
    return None


# def analyze_pydantic(
#     field_type: StructureAnalysis, expression: TypeExpression
# ) -> PydanticFieldAnalysis | None:
#     """Analyze a Pydantic field definition from type analysis and expressions.

#     Args:
#         field_type (StructureAnalysis): The structure analysis of the field type.
#         expression (TypeExpression): The type expression to analyze.

#     Returns:
#         PydanticFieldAnalysis | None: The pydantic field analysis result, or None if the
#             expression is not a Pydantic Field.
#     """
#     is_required = _is_field_required(field_type)

#     if (
#         isinstance(expression, CallStructureAnalysis)
#         and isinstance(expression.function, NameStructureAnalysis)
#         and expression.function.name == "Field"
#     ):
#         description = None
#         alias = None
#         default = None
#         for argument in expression.arguments:
#             if isinstance(argument, KeywordStructureAnalysis):
#                 match argument.name:
#                     case "description":
#                         description = retrieve_str_value(argument.value)

#                     case "alias":
#                         alias = retrieve_str_value(argument.value)
#             else:
#                 default = retrieve_str_value(argument)

#         return PydanticFieldAnalysis(
#             required=is_required,
#             description=description,
#             alias=alias,
#             default_source=default,
#         )
#     return None


def analyze_pydantic(
    field_type: StructureAnalysis, expression: ExpressionAnalysis
) -> PydanticFieldAnalysis | None:
    """Analyze a Pydantic field definition from type analysis and expressions.

    Args:
        field_type (StructureAnalysis): The structure analysis of the field type.
        expression (TypeExpression): The type expression to analyze.

    Returns:
        PydanticFieldAnalysis | None: The pydantic field analysis result, or None if the
            expression is not a Pydantic Field.
    """
    is_required = _is_field_required(field_type)

    if (
        isinstance(expression, CallExpressionAnalysis)
        and isinstance(expression.func, NameExpressionAnalysis)
        and expression.func.name == "Field"
    ):
        description = None
        alias = None
        default = None
        for argument in expression.keywords:
            match argument.arg:
                case "description":
                    description = retrieve_str_value(argument.value)

                case "alias":
                    alias = retrieve_str_value(argument.value)
                case "default":
                    default = retrieve_str_value(argument.value)
        if len(expression.args) > 0:
            first_arg = expression.args[0]
            default = retrieve_str_value(first_arg)

        return PydanticFieldAnalysis(
            required=is_required,
            description=description,
            alias=alias,
            default_source=default,
        )
    return None


ast_value_expression: ExpressionAnalysis


def get_pydantic_field_from_annotated_type_expression(
    expression: TypeExpression | None,
    ast_expression: ExpressionAnalysis | None,
) -> tuple[TypeExpression, CallExpressionAnalysis] | None:
    """Extract a Pydantic Field call structure and its underlying type from an Annotated
    type expression.

    Args:
        expression (TypeExpression | None): The type expression to inspect, or None.

    Returns:
        tuple[TypeExpression, CallStructureAnalysis] | None: A tuple containing the
            assumed type and the Field call structure analysis, or None if not found.
    """
    if not isinstance(expression, GenericsStructureAnalysis):
        return None

    if not (
        isinstance(expression.base, NameStructureAnalysis)
        and expression.base.name == "Annotated"
    ):
        return None
    if not isinstance(ast_expression, SubscriptExpressionAnalysis):
        return None
    ast_value = ast_expression.value
    if not (
        isinstance(ast_value, NameExpressionAnalysis) and ast_value.name == "Annotated"
    ):
        return None

    ast_slice = ast_expression.slice
    if not (isinstance(ast_slice, TupleExpressionAnalysis)):
        return None

    parameters = expression.parameters
    if len(parameters) < 2:
        return None

    assumed_type = parameters[0]

    for element in ast_slice.elements:
        if (
            isinstance(element, CallExpressionAnalysis)
            and isinstance(element.func, NameExpressionAnalysis)
            and element.func.name == "Field"
        ):
            return assumed_type, element

    return None
