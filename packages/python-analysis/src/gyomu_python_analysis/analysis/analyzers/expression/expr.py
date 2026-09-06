import ast

from griffe import (
    Expr,
    ExprAttribute,
    ExprBinOp,
    ExprCall,
    ExprConstant,
    ExprDict,
    ExprKeyword,
    ExprList,
    ExprName,
    ExprSet,
    ExprSubscript,
    ExprTuple,
)
from gyomu_schema.schemas.python.type.structure import (
    EllipsisStructureAnalysis,
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
    CallStructureAnalysis,
    DictionaryStructureAnalysis,
    ExpressionAnalysis,
    GenericsStructureAnalysis,
    KeywordStructureAnalysis,
    LiteralStructureAnalysis,
    SetStructureAnalysis,
    TupleStructureAnalysis,
    TypeExpression,
    UnionStructureAnalysis,
)

from gyomu_python_analysis.analysis.analyzers.context import SymbolContext


def analyze_expression(expression: Expr, context: SymbolContext) -> ExpressionAnalysis:
    if isinstance(expression, ExprName):
        return analyze_expression_name(expression, context)
    if isinstance(expression, ExprBinOp):
        return _analyze_expression_binary_operation(expression, context)
    if isinstance(expression, ExprSubscript):
        return analyze_subscript(expression, context)
    if isinstance(expression, ExprAttribute):
        return _analyze_expression_attribute(expression, context)
    if isinstance(expression, ExprTuple):
        return analyze_tuple(expression, context)
    if isinstance(expression, ExprList):
        return analyze_array(expression, context)
    if isinstance(expression, ExprDict):
        return analyze_dictionary(expression, context)
    if isinstance(expression, ExprSet):
        return analyze_set(expression, context)
    if isinstance(expression, ExprKeyword):
        return _analyze_keyword(expression, context)
    if isinstance(expression, ExprCall):
        return _analyze_call(expression, context)

    else:
        print(f"Unsupported expression type: {type(expression)}")
        print(expression.as_dict())
        return UnknownStructureAnalysis()
    # elif isinstance(expression, ExprSubscript):
    #     return analyze_expression_subscript(expression)
    # else:
    #     raise ValueError(f"Unsupported expression type: {type(expression)}")


def analyze_expression_constant(
    expression: ExprConstant, context: SymbolContext
) -> TypeExpression:
    return analyze_type_expression(expression.value, context)


def _analyze_expression_attribute(
    expression: ExprAttribute, context: SymbolContext
) -> AttributeStructureAnalysis:
    # print(
    #     dict(
    #         canonical_path=expression.canonical_path,
    #         values=expression.values,
    #         path=expression.path,
    #         canonical_name=expression.canonical_name,
    #         is_classvar=expression.is_classvar,
    #         is_generator=expression.is_generator,
    #         is_iterator=expression.is_iterator,
    #         is_tuple=expression.is_tuple,
    #     )
    # )
    return AttributeStructureAnalysis(
        values=tuple(
            [
                analyzed
                for value in expression.values
                if (analyzed := analyze_type_expression(value, context)) is not None
            ]
        )
    )


def _analyze_expression_binary_operation(
    expression: ExprBinOp, context: SymbolContext
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
            return _analyze_union(expression, context)
        case _:
            print(f"Unsupported operation: {type(expression)}")
            print(expression.as_dict())
            return UnknownStructureAnalysis()


def _analyze_union(
    expression: ExprBinOp, context: SymbolContext
) -> UnionStructureAnalysis:
    types: list[TypeExpression] = []

    def append_union_types(value: str | Expr) -> None:
        if isinstance(value, ExprBinOp) and value.operator == "|":
            append_union_types(value.left)
            append_union_types(value.right)
            return

        analyzed = analyze_type_expression(value, context)
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


def analyze_subscript(
    expression: ExprSubscript, context: SymbolContext
) -> ExpressionAnalysis:
    # print(expression.as_dict())
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
            return analyze_literal(slice, context)
        elif left.name == "list":
            return _analyze_array_from_subscript(slice, context)
        elif left.name == "dict":
            return _analyze_dictionary_from_subscript(slice, context)
        elif left.name == "Callable":
            return _analyze_callable_from_subscript(slice, context)
        elif left.name == "tuple":
            return _analyze_tuple_from_subscript(slice, context)
        elif left.name == "set":
            return _analyze_set_from_subscript(slice, context)

    param = analyze_type_expression(slice, context)
    if not isinstance(param, LiteralValue):
        parameters: list[TypeExpression] = []
        if isinstance(param, TupleStructureAnalysis):
            parameters = list(param.elements)
        elif isinstance(param, NameStructureAnalysis):
            parameters.append(param)
        else:
            parameters.append(param)
        return GenericsStructureAnalysis(
            base=analyze_type_expression(left, context), parameters=tuple(parameters)
        )
    print(f"Unsupported expression type in subscript: {type(expression)}")
    print(expression.as_dict())
    return UnknownStructureAnalysis()


def analyze_dictionary(
    expression: ExprDict, context: SymbolContext
) -> DictionaryStructureAnalysis:
    assert len(expression.keys) == 1
    assert expression.keys[0]
    assert len(expression.values) == 1
    return DictionaryStructureAnalysis(
        keys=analyze_type_expression(expression.keys[0], context),
        values=analyze_type_expression(expression.values[0], context),
    )


def _analyze_dictionary_from_subscript(
    slice: str | Expr, context: SymbolContext
) -> DictionaryStructureAnalysis:
    assert isinstance(slice, ExprTuple)
    assert len(slice.elements) == 2
    return DictionaryStructureAnalysis(
        keys=analyze_type_expression(slice.elements[0], context),
        values=analyze_type_expression(slice.elements[1], context),
    )


def analyze_array(
    expression: ExprList, context: SymbolContext
) -> ArrayStructureAnalysis:
    return ArrayStructureAnalysis(
        element=analyze_type_expression(expression.elements[0], context)
    )


def _analyze_callable_from_subscript(
    slice: str | Expr, context: SymbolContext
) -> CallableStructureAnalysis:
    assert isinstance(slice, ExprTuple)
    assert len(slice.elements) == 2
    parameters_expression = slice.elements[0]
    if isinstance(parameters_expression, ExprList):
        parameters: list[TypeExpression] = []
        for expression in parameters_expression.elements:
            analyzed = analyze_type_expression(expression, context)
            parameters.append(analyzed)

        return CallableStructureAnalysis(
            parameters=tuple(parameters),
            return_type=analyze_type_expression(slice.elements[1], context),
        )
    assert isinstance(parameters_expression, str)
    assert parameters_expression == "..."
    return CallableStructureAnalysis(
        parameters=None,
        return_type=analyze_type_expression(slice.elements[1], context),
    )


def _analyze_array_from_subscript(
    slice: str | Expr, context: SymbolContext
) -> ArrayStructureAnalysis:
    return ArrayStructureAnalysis(element=analyze_type_expression(slice, context))


def analyze_literal(
    slice: str | Expr, context: SymbolContext
) -> LiteralStructureAnalysis:

    return LiteralStructureAnalysis(value=analyze_type_expression(slice, context))


def analyze_type_expression(
    value: str | Expr, context: SymbolContext
) -> TypeExpression:
    if isinstance(value, str):
        parsed = ast.literal_eval(value)
        if parsed is None:
            return NoneStructureAnalysis()
        if parsed is Ellipsis:
            return EllipsisStructureAnalysis()
        return LiteralValue(value=parse_literal_value(value))
    return analyze_expression(value, context)


def parse_literal_value(value: str) -> str | int | bool:
    parsed = ast.literal_eval(value)
    if isinstance(parsed, bool):
        return parsed

    if isinstance(parsed, int):
        return parsed

    if isinstance(parsed, str):
        return parsed

    raise ValueError(f"Unsupported literal value: {value}")


def _analyze_tuple_from_subscript(
    slice: str | Expr, context: SymbolContext
) -> TupleStructureAnalysis:
    assert isinstance(slice, ExprTuple)

    return analyze_tuple(slice, context)


def analyze_tuple(
    expression: ExprTuple, context: SymbolContext
) -> TupleStructureAnalysis:
    variable_length = False
    elements: list[TypeExpression] = []

    for value in expression.elements:
        if value == "...":
            variable_length = True
            continue

        analyzed = analyze_type_expression(value, context)
        if analyzed is not None:
            elements.append(analyzed)

    return TupleStructureAnalysis(
        elements=tuple(elements),
        variable_length=variable_length,
    )


def _analyze_set_from_subscript(
    slice: str | Expr, context: SymbolContext
) -> SetStructureAnalysis:
    return SetStructureAnalysis(element_type=analyze_type_expression(slice, context))


def analyze_set(expression: ExprSet, context: SymbolContext) -> SetStructureAnalysis:
    return SetStructureAnalysis(
        element_type=analyze_type_expression(expression.elements[0], context)
    )


def analyze_expression_name(
    expression: ExprName, context: SymbolContext
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


def _analyze_keyword(
    expression: ExprKeyword, context: SymbolContext
) -> KeywordStructureAnalysis:
    name = expression.name
    value = analyze_type_expression(expression.value, context)
    return KeywordStructureAnalysis(name=name, value=value)


def _analyze_call(
    expression: ExprCall, context: SymbolContext
) -> CallStructureAnalysis:
    func = analyze_expression(expression.function, context)
    arguments: list[TypeExpression] = []

    for value in expression.arguments:
        analyzed = analyze_type_expression(value, context)
        arguments.append(analyzed)

    return CallStructureAnalysis(function=func, arguments=tuple(arguments))
