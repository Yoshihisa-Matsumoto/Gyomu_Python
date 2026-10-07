from gyomu_schema.schemas.python.pydantic import PydanticFieldAnalysis
from gyomu_schema.schemas.python.type.expression import (
    BinaryOperator,
    BinOpExpressionAnalysis,
    CallExpressionAnalysis,
    ExpressionAnalysis,
    NameExpressionAnalysis,
    NoneExpressionAnalysis,
    SubscriptExpressionAnalysis,
    TupleExpressionAnalysis,
)
from gyomu_schema.schemas.python.type.structure import (
    LiteralValue,
    NoneStructureAnalysis,
)
from gyomu_schema.schemas.python.type.type_analysis import (
    StructureAnalysis,
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

    return _analyze_pydantic(is_required=is_required, expression=expression)


def _analyze_pydantic(
    is_required: bool, expression: ExpressionAnalysis
) -> PydanticFieldAnalysis | None:
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


def get_pydantic_from_value_only(
    ast_expression: ExpressionAnalysis,
) -> PydanticFieldAnalysis | None:
    """Extract a Pydantic Field call structure and its underlying type from an Annotated
    type expression.

    Args:
        expression (TypeExpression | None): The type expression to inspect, or None.
        ast_expression (ExpressionAnalysis | None): The AST expression to inspect, or
            None.

    Returns:
        tuple[TypeExpression, CallExpressionAnalysis] | None: A tuple containing the
            assumed type and the Field call structure analysis, or None if not found.
    """
    if not (
        isinstance(ast_expression, SubscriptExpressionAnalysis)
        and isinstance(ast_expression.value, NameExpressionAnalysis)
        and ast_expression.value.name == "Annotated"
    ):
        return None

    ast_slice = ast_expression.slice
    if not (isinstance(ast_slice, TupleExpressionAnalysis)):
        return None

    parameters = ast_slice.elements
    if len(parameters) < 2:
        return None

    assumed_type = parameters[0]
    is_required = _is_field_required_from_assumed_type(assumed_type)

    for element in ast_slice.elements:
        if (
            isinstance(element, CallExpressionAnalysis)
            and isinstance(element.func, NameExpressionAnalysis)
            and element.func.name == "Field"
        ):
            return _analyze_pydantic(is_required=is_required, expression=element)

    return None


def _is_field_required_from_assumed_type(assumed_type: ExpressionAnalysis) -> bool:
    if isinstance(assumed_type, NameExpressionAnalysis):
        return assumed_type.name != "None"

    if isinstance(assumed_type, NoneExpressionAnalysis):
        return False
    if isinstance(assumed_type, BinOpExpressionAnalysis):
        return not _is_binop_include_none(assumed_type)
    return True


def _is_binop_include_none(binop: BinOpExpressionAnalysis) -> bool:
    if binop.op != BinaryOperator.BIT_OR:
        return False

    is_none_included = False
    if _is_expression_none(binop.left):
        is_none_included = True

    if _is_expression_none(binop.right):
        is_none_included = True

    return is_none_included


def _is_expression_none(expression: ExpressionAnalysis) -> bool:
    if isinstance(expression, NameExpressionAnalysis):
        return expression.name == "None"

    if isinstance(expression, NoneExpressionAnalysis):
        return True
    if isinstance(expression, BinOpExpressionAnalysis):
        return _is_binop_include_none(expression)
    return False
