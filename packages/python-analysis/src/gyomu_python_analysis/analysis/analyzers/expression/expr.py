import ast

from griffe import (
    Expr,
    ExprAttribute,
    ExprBinOp,
    ExprConstant,
    ExprDict,
    ExprList,
    ExprName,
    ExprSubscript,
    ExprTuple,
)
from gyomu_python_analysis.analysis.analyzers.expression.name import (
    analyze_expression_name,
)
from gyomu_schema.schemas.python.type.structure import (
    LiteralValue,
    NoneStructureAnalysis,
    UnknownStructureAnalysis,
)
from gyomu_schema.schemas.python.type.type_analysis import (
    ArrayStructureAnalysis,
    AttributeStructureAnalysis,
    CallableStructureAnalysis,
    DictionaryStructureAnalysis,
    ExpressionAnalysis,
    LiteralStructureAnalysis,
    TupleStructureAnalysis,
    TypeAnalysis,
    TypeExpression,
    UnionStructureAnalysis,
)


def analyze_expression(expression: Expr) -> ExpressionAnalysis:
    if isinstance(expression, ExprName):
        return analyze_expression_name(expression)
    if isinstance(expression, ExprBinOp):
        return _analyze_expression_binary_operation(expression)
    if isinstance(expression, ExprSubscript):
        return analyze_subscript(expression)
    if isinstance(expression, ExprAttribute):
        return _analyze_expression_attribute(expression)
    if isinstance(expression, ExprTuple):
        return analyze_tuple(expression)
    if isinstance(expression, ExprList):
        return analyze_array(expression)
    if isinstance(expression, ExprDict):
        return analyze_dictionary(expression)

    else:
        print(f"Unsupported expression type: {type(expression)}")
        print(expression.as_dict())
        return UnknownStructureAnalysis()
    # elif isinstance(expression, ExprSubscript):
    #     return analyze_expression_subscript(expression)
    # else:
    #     raise ValueError(f"Unsupported expression type: {type(expression)}")


def analyze_expression_constant(expression: ExprConstant) -> TypeExpression:
    return analyze_type_expression(expression.value)


def _analyze_expression_attribute(
    expression: ExprAttribute,
) -> AttributeStructureAnalysis:
    print(
        dict(
            canonical_path=expression.canonical_path,
            values=expression.values,
            path=expression.path,
            canonical_name=expression.canonical_name,
            is_classvar=expression.is_classvar,
            is_generator=expression.is_generator,
            is_iterator=expression.is_iterator,
            is_tuple=expression.is_tuple,
        )
    )
    return AttributeStructureAnalysis(
        values=tuple(
            [
                analyzed
                for value in expression.values
                if (analyzed := _analyze_type_internal(value)) is not None
            ]
        )
    )


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
            print(f"Unsupported expression type: {type(expression)}")
            print(expression.as_dict())
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


def analyze_subscript(expression: ExprSubscript) -> ExpressionAnalysis:
    print(expression.as_dict())
    # print(f"canonical_name  : {expression.canonical_name}")
    # print(f"canonical_path  : {expression.canonical_path}")
    # print(f"classname : {expression.classname}")
    # print(f"is_classvar: {expression.is_classvar}")
    # print(f"is_generator: {expression.is_generator}")
    # print(f"is_iterator: {expression.is_iterator}")
    # print(f"is_tuple : {expression.is_tuple}")

    left = expression.left
    slice = expression.slice
    if isinstance(left, ExprName):
        if left.name == "Literal":
            return analyze_literal(slice)
        elif left.name == "list":
            return _analyze_array_from_subscript(slice)
        elif left.name == "dict":
            return _analyze_dictionary_from_subscript(slice)
        elif left.name == "Callable":
            return _analyze_callable_from_subscript(slice)

    print(f"Unsupported expression type in subscript: {type(expression)}")
    print(expression.as_dict())
    return UnknownStructureAnalysis()


def analyze_dictionary(expression: ExprDict) -> DictionaryStructureAnalysis:
    assert len(expression.keys) == 1
    assert expression.keys[0]
    assert len(expression.values) == 1
    return DictionaryStructureAnalysis(
        keys=analyze_type_expression(expression.keys[0]),
        values=analyze_type_expression(expression.values[0]),
    )


def _analyze_dictionary_from_subscript(
    slice: str | Expr,
) -> DictionaryStructureAnalysis:
    assert isinstance(slice, ExprTuple)
    assert len(slice.elements) == 2
    return DictionaryStructureAnalysis(
        keys=analyze_type_expression(slice.elements[0]),
        values=analyze_type_expression(slice.elements[1]),
    )


def analyze_array(expression: ExprList) -> ArrayStructureAnalysis:
    return ArrayStructureAnalysis(
        element=analyze_type_expression(expression.elements[0])
    )


def _analyze_callable_from_subscript(slice: str | Expr) -> CallableStructureAnalysis:
    assert isinstance(slice, ExprTuple)
    assert len(slice.elements) == 2
    parameters_expression = slice.elements[0]
    if isinstance(parameters_expression, ExprList):
        parameters: list[TypeAnalysis] = []
        for expression in parameters_expression.elements:
            analyzed = _analyze_type_internal(expression)
            parameters.append(analyzed)

        return CallableStructureAnalysis(
            parameters=tuple(parameters),
            return_type=_analyze_type_internal(slice.elements[1]),
        )
    assert isinstance(parameters_expression, str)
    assert parameters_expression == "..."
    return CallableStructureAnalysis(
        parameters=None,
        return_type=_analyze_type_internal(slice.elements[1]),
    )


def _analyze_array_from_subscript(slice: str | Expr) -> ArrayStructureAnalysis:
    return ArrayStructureAnalysis(element=analyze_type_expression(slice))


def analyze_literal(slice: str | Expr) -> LiteralStructureAnalysis:

    return LiteralStructureAnalysis(value=analyze_type_expression(slice))


def analyze_type_expression(value: str | Expr) -> TypeExpression:
    if isinstance(value, str):
        return LiteralValue(value=parse_literal_value(value))
    return analyze_expression(value)


def parse_literal_value(value: str) -> str | int | bool:
    parsed = ast.literal_eval(value)
    if isinstance(parsed, bool):
        return parsed

    if isinstance(parsed, int):
        return parsed

    if isinstance(parsed, str):
        return parsed

    raise ValueError(f"Unsupported literal value: {value}")


def analyze_tuple(expression: ExprTuple) -> TupleStructureAnalysis:
    return TupleStructureAnalysis(
        elements=[
            analyzed
            for value in expression.elements
            if (analyzed := analyze_type_expression(value))
        ]
    )
