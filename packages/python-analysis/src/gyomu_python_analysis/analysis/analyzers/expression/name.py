from griffe import ExprName
from gyomu_schema.schemas.python.type.structure import (
    NameStructureAnalysis,
    NoneStructureAnalysis,
    TypeStructureKind,
)


def analyze_expression_name(
    expression: ExprName,
) -> NameStructureAnalysis | NoneStructureAnalysis:
    # print(
    #     dict(
    #         name=expression.name,
    #         member=expression.member,
    #         path=expression.path,
    #         canonical_name=expression.canonical_name,
    #         is_enum_class=expression.is_enum_class,
    #         is_enum_instance=expression.is_enum_instance,
    #         is_enum_value=expression.is_enum_value,
    #         is_type_parameter=expression.is_type_parameter,
    #     )
    # )
    if expression.name == "None":
        return NoneStructureAnalysis(
            kind=TypeStructureKind.NONE,
        )
    return NameStructureAnalysis(
        name=expression.name,
    )
