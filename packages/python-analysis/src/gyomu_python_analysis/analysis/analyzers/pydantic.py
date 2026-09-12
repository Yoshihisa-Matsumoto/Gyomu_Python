from gyomu_schema.schemas.python.pydantic import PydanticFieldAnalysis
from gyomu_schema.schemas.python.type.structure import (
    LiteralValue,
    NameStructureAnalysis,
    NoneStructureAnalysis,
)
from gyomu_schema.schemas.python.type.type_analysis import (
    CallStructureAnalysis,
    ExpressionAnalysis,
    KeywordStructureAnalysis,
    TypeExpression,
    UnionStructureAnalysis,
)


def _is_field_required(field_type: ExpressionAnalysis) -> bool:
    if isinstance(field_type, NoneStructureAnalysis):
        return False
    if isinstance(field_type, UnionStructureAnalysis):
        for element in field_type.types:
            if isinstance(element, NoneStructureAnalysis):
                return False
    return True


def retrieve_str_value(value: TypeExpression) -> str | None:
    if isinstance(value, LiteralValue):
        return str(value.value)
    return None


def analyze_pydantic(
    field_type: ExpressionAnalysis, expression: TypeExpression
) -> PydanticFieldAnalysis | None:
    is_required = _is_field_required(field_type)

    if (
        isinstance(expression, CallStructureAnalysis)
        and isinstance(expression.function, NameStructureAnalysis)
        and expression.function.name == "Field"
    ):
        description = None
        alias = None
        default = None
        for argument in expression.arguments:
            if isinstance(argument, KeywordStructureAnalysis):
                match argument.name:
                    case "description":
                        description = retrieve_str_value(argument.value)

                    case "alias":
                        alias = retrieve_str_value(argument.value)
            else:
                default = retrieve_str_value(argument)

        return PydanticFieldAnalysis(
            required=is_required,
            description=description,
            alias=alias,
            default_source=default,
        )
    return None
