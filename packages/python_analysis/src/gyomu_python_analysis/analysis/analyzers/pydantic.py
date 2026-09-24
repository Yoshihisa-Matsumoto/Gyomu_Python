from gyomu_schema.schemas.python.pydantic import PydanticFieldAnalysis
from gyomu_schema.schemas.python.type.structure import (
    LiteralValue,
    NameStructureAnalysis,
    NoneStructureAnalysis,
)
from gyomu_schema.schemas.python.type.type_analysis import (
    CallStructureAnalysis,
    GenericsStructureAnalysis,
    KeywordStructureAnalysis,
    StructureAnalysis,
    TypeExpression,
    UnionStructureAnalysis,
)


def _is_field_required(field_type: StructureAnalysis) -> bool:
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
    field_type: StructureAnalysis, expression: TypeExpression
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


def get_pydantic_field_from_annotated_type_expression(
    expression: TypeExpression | None,
) -> tuple[TypeExpression, CallStructureAnalysis] | None:
    if not isinstance(expression, GenericsStructureAnalysis):
        return None

    if not (
        isinstance(expression.base, NameStructureAnalysis)
        and expression.base.name == "Annotated"
    ):
        return None

    parameters = expression.parameters
    if len(parameters) < 2:
        return None

    assumed_type = parameters[0]

    for metadata in parameters[1:]:
        if (
            isinstance(metadata, CallStructureAnalysis)
            and isinstance(metadata.function, NameStructureAnalysis)
            and metadata.function.name == "Field"
        ):
            return assumed_type, metadata

    return None
