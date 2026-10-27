import json

from gyomu_schema.schemas.python.type.structure import (
    EllipsisStructureAnalysis,
    LiteralValue,
    NameStructureAnalysis,
    NoneStructureAnalysis,
)
from gyomu_schema.schemas.python.type.type_analysis import (
    ArrayStructureAnalysis,
    AttributeStructureAnalysis,
    CallableStructureAnalysis,
    CallStructureAnalysis,
    DictionaryStructureAnalysis,
    GenericsStructureAnalysis,
    KeywordStructureAnalysis,
    LiteralStructureAnalysis,
    SetStructureAnalysis,
    StructureAnalysis,
    TupleStructureAnalysis,
    TypeAnalysis,
    TypeExpression,
    UnionStructureAnalysis,
)


def _convert_literal_to_code(
    value: str | bytes | bool | int | float | complex | None,
) -> str:
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)

    return repr(value)


def _convert_type_expression(expression: TypeExpression, class_name: str | None) -> str:
    if isinstance(expression, LiteralValue):
        return _convert_literal_to_code(expression.value)
    else:
        return _convert_structure(expression, class_name)


def _convert_structure(structure: StructureAnalysis, class_name: str | None) -> str:
    if isinstance(structure, NameStructureAnalysis):
        if structure.name == "Self":
            return class_name if class_name is not None else structure.name
        return structure.name
    if isinstance(structure, NoneStructureAnalysis):
        return "None"
    if isinstance(structure, LiteralStructureAnalysis):
        if isinstance(structure.value, TupleStructureAnalysis):
            elements = ", ".join(
                _convert_type_expression(type_analysis, class_name)
                for type_analysis in structure.value.elements
            )
            return f"Literal[{elements}]"
        literal_value = _convert_type_expression(structure.value, class_name)
        return f"Literal[{literal_value}]"
    if isinstance(structure, EllipsisStructureAnalysis):
        return "..."
    if isinstance(structure, UnionStructureAnalysis):
        return " | ".join(
            _convert_type_expression(type_analysis, class_name)
            for type_analysis in structure.types
        )

    if isinstance(structure, AttributeStructureAnalysis):
        return ".".join(
            _convert_type_expression(type_analysis, class_name)
            for type_analysis in structure.values
        )
    if isinstance(structure, TupleStructureAnalysis):
        elements = ", ".join(
            _convert_type_expression(type_analysis, class_name)
            for type_analysis in structure.elements
        )
        if structure.variable_length:
            elements = elements + ", ..." if len(elements) > 0 else "..."
        return f"tuple[{elements}]"
    if isinstance(structure, ArrayStructureAnalysis):
        return f"list[{_convert_type_expression(structure.element, class_name)}]"
    if isinstance(structure, DictionaryStructureAnalysis):
        if structure.keys is None:
            if structure.values is None:
                return "dict"
            else:
                return (
                    "dict[Any, "
                    f"{_convert_type_expression(structure.values, class_name)}]"
                )
        elif structure.values is None:
            return f"dict[{_convert_type_expression(structure.keys, class_name)}, Any]"
        else:
            return (
                f"dict[{_convert_type_expression(structure.keys, class_name)}, "
                f"{_convert_type_expression(structure.values, class_name)}]"
            )
    if isinstance(structure, GenericsStructureAnalysis):
        params = ", ".join(
            _convert_type_expression(type_analysis, class_name)
            for type_analysis in structure.parameters
        )
        return f"{_convert_type_expression(structure.base, class_name)}[{params}]"
    if isinstance(structure, SetStructureAnalysis):
        return f"set[{_convert_type_expression(structure.element_type, class_name)}]"
    if isinstance(structure, KeywordStructureAnalysis):
        return (
            f"{structure.name}: {_convert_type_expression(structure.value, class_name)}"
        )
    if isinstance(structure, CallableStructureAnalysis):
        params = (
            (
                "["
                + ", ".join(
                    _convert_type_expression(type_analysis, class_name)
                    for type_analysis in structure.parameters
                )
                + "]"
            )
            if structure.parameters is not None
            else "..."
        )
        return (
            f"Callable[{params}, "
            f"{_convert_type_expression(structure.return_type, class_name)}]"
        )
    if isinstance(structure, CallStructureAnalysis):
        function = _convert_type_expression(structure.function, class_name)
        arguments = ", ".join(
            _convert_type_expression(argument, class_name)
            for argument in structure.arguments
        )
        return f"{function}({arguments})"
    else:
        raise ValueError(f"Unsupported Type: {type(structure).__name__}")


def dump_type(type_analysis: TypeAnalysis, class_name: str | None = None) -> str:
    if type_analysis.structure is None:
        return type_analysis.text
    structure = type_analysis.structure
    return _convert_structure(structure, class_name)
