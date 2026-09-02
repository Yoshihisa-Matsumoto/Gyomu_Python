from griffe import Expr, ExprBinOp, ExprName
from gyomu_python_analysis.analysis.analyzers.expression.name import (
    analyze_expression_name,
)
from gyomu_schema.schemas.python.type.structure import (
    NoneStructureAnalysis,
    UnknownStructureAnalysis,
)
from gyomu_schema.schemas.python.type.type_analysis import (
    TypeAnalysis,
    TypeStructureAnalysis,
    UnionStructureAnalysis,
)


def analyze_expression(expression: Expr) -> TypeStructureAnalysis | None:
    if isinstance(expression, ExprName):
        return analyze_expression_name(expression)
    if isinstance(expression, ExprBinOp):
        return _analyze_expression_binary_operation(expression)
    # elif isinstance(expression, ExprSubscript):
    #     return analyze_expression_subscript(expression)
    # else:
    #     raise ValueError(f"Unsupported expression type: {type(expression)}")


def _analyze_expression_binary_operation(
    expression: ExprBinOp,
) -> UnionStructureAnalysis | UnknownStructureAnalysis:
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
    match expression.operator:
        case "|":
            return _analyze_union(expression)
        case _:
            return UnknownStructureAnalysis()


def _analyze_union(expression: ExprBinOp) -> UnionStructureAnalysis:
    left = expression.left
    right = expression.right
    types: list[TypeAnalysis] = []

    analyze_left = _analyze_type_internal(left)
    if analyze_left is not None:
        types.append(analyze_left)
    analyze_right = _analyze_type_internal(right)
    if analyze_right is not None:
        types.append(analyze_right)
    return UnionStructureAnalysis(
        types=tuple(types),
    )
    return _analyze_union(expression)


def _analyze_type_internal(annotation: str | Expr) -> TypeAnalysis:
    if isinstance(annotation, str):
        print(annotation)
        if annotation == "None":
            return TypeAnalysis(text=annotation, structure=NoneStructureAnalysis())
        return TypeAnalysis(text=annotation)
    if isinstance(annotation, Expr):
        text = str(annotation)
        print(annotation.as_dict())
        return TypeAnalysis(text=text, structure=analyze_expression(annotation))
