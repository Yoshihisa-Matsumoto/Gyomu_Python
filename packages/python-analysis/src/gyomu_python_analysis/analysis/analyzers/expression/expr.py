import ast

from griffe import (
    Expr,
    ExprAttribute,
    ExprBinOp,
    ExprConstant,
    ExprDict,
    ExprList,
    ExprName,
    ExprSet,
    ExprSubscript,
    ExprTuple,
)
from gyomu_schema.schemas.python.type.structure import (
    LiteralValue,
    NameStructureAnalysis,
    NoneStructureAnalysis,
    TypeStructureKind,
    UnknownStructureAnalysis,
)
from gyomu_schema.schemas.python.type.type_analysis import (
    ArrayStructureAnalysis,
    AttributeStructureAnalysis,
    CallableStructureAnalysis,
    DictionaryStructureAnalysis,
    ExpressionAnalysis,
    GenericsStructureAnalysis,
    LiteralStructureAnalysis,
    SetStructureAnalysis,
    TupleStructureAnalysis,
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
    if isinstance(expression, ExprSet):
        return analyze_set(expression)

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
                if (analyzed := analyze_type_expression(value)) is not None
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
            print(f"Unsupported operation: {type(expression)}")
            print(expression.as_dict())
            return UnknownStructureAnalysis()


def _analyze_union(expression: ExprBinOp) -> UnionStructureAnalysis:
    types: list[TypeExpression] = []

    def append_union_types(value: str | Expr) -> None:
        if isinstance(value, ExprBinOp) and value.operator == "|":
            append_union_types(value.left)
            append_union_types(value.right)
            return

        analyzed = analyze_type_expression(value)
        types.append(analyzed)

    append_union_types(expression)

    return UnionStructureAnalysis(
        types=tuple(types),
    )


# def _analyze_type_internal(annotation: str | Expr) -> TypeAnalysis:
#     if isinstance(annotation, str):
#         print(annotation)
#         if annotation == "None":
#             return TypeAnalysis(text=annotation, structure=NoneStructureAnalysis())
#         return TypeAnalysis(text=annotation)
#     if isinstance(annotation, Expr):
#         text = str(annotation)
#         print(annotation.as_dict())
#         return TypeAnalysis(text=text, structure=analyze_expression(annotation))


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
        elif left.name == "tuple":
            return _analyze_tuple_from_subscript(slice)
        elif left.name == "set":
            return _analyze_set_from_subscript(slice)

    param = analyze_type_expression(slice)
    if not isinstance(param, LiteralValue):
        parameters: list[TypeExpression] = []
        if isinstance(param, TupleStructureAnalysis):
            parameters = list(param.elements)
        elif isinstance(param, NameStructureAnalysis):
            parameters.append(param)
        else:
            parameters.append(param)
        return GenericsStructureAnalysis(
            base=analyze_type_expression(left), parameters=tuple(parameters)
        )
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
        parameters: list[TypeExpression] = []
        for expression in parameters_expression.elements:
            analyzed = analyze_type_expression(expression)
            parameters.append(analyzed)

        return CallableStructureAnalysis(
            parameters=tuple(parameters),
            return_type=analyze_type_expression(slice.elements[1]),
        )
    assert isinstance(parameters_expression, str)
    assert parameters_expression == "..."
    return CallableStructureAnalysis(
        parameters=None,
        return_type=analyze_type_expression(slice.elements[1]),
    )


def _analyze_array_from_subscript(slice: str | Expr) -> ArrayStructureAnalysis:
    return ArrayStructureAnalysis(element=analyze_type_expression(slice))


def analyze_literal(slice: str | Expr) -> LiteralStructureAnalysis:

    return LiteralStructureAnalysis(value=analyze_type_expression(slice))


def analyze_type_expression(value: str | Expr) -> TypeExpression:
    if isinstance(value, str):
        parsed = ast.literal_eval(value)
        if parsed is None:
            return NoneStructureAnalysis()
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


def _analyze_tuple_from_subscript(slice: str | Expr) -> TupleStructureAnalysis:
    assert isinstance(slice, ExprTuple)

    return analyze_tuple(slice)


def analyze_tuple(expression: ExprTuple) -> TupleStructureAnalysis:
    variable_length = False
    elements: list[TypeExpression] = []

    for value in expression.elements:
        if value == "...":
            variable_length = True
            continue

        analyzed = analyze_type_expression(value)
        if analyzed is not None:
            elements.append(analyzed)

    return TupleStructureAnalysis(
        elements=tuple(elements),
        variable_length=variable_length,
    )


def _analyze_set_from_subscript(slice: str | Expr) -> SetStructureAnalysis:
    return SetStructureAnalysis(element_type=analyze_type_expression(slice))


def analyze_set(expression: ExprSet) -> SetStructureAnalysis:
    return SetStructureAnalysis(
        element_type=analyze_type_expression(expression.elements[0])
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
