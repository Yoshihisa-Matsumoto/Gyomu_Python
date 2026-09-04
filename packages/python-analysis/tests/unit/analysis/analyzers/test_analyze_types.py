from griffe import Attribute
from gyomu_python_analysis.analysis.analyzers.types import analyze_type
from gyomu_python_analysis.analysis.analyzers.variables import analyze_variable
from gyomu_schema.schemas.python.type.structure import (
    LiteralValue,
    NameStructureAnalysis,
    NoneStructureAnalysis,
)
from gyomu_schema.schemas.python.type.type_analysis import (
    ArrayStructureAnalysis,
    CallableStructureAnalysis,
    DictionaryStructureAnalysis,
    GenericsStructureAnalysis,
    LiteralStructureAnalysis,
    SetStructureAnalysis,
    TupleStructureAnalysis,
    UnionStructureAnalysis,
)
from gyomu_schema.schemas.python.types import PythonPath
from gyomu_schema.schemas.python.variable import VariableAnalysis

from tests.helpers import AnalysisTestBase


def test_analyze_type_returns_none_for_none() -> None:
    assert analyze_type(None) is None


def test_analyze_type_analyzes_none_string() -> None:
    result = analyze_type("None")

    assert result is not None
    assert result.text == "None"
    assert isinstance(result.structure, NoneStructureAnalysis)


def test_analyze_type_preserves_string_annotation() -> None:
    result = analyze_type("MyType")

    assert result is not None
    assert result.text == "MyType"
    assert result.structure is None


class TestAnalyzeType(AnalysisTestBase):
    def _analyze_variable_internal(
        self, name: str, module_name: PythonPath
    ) -> VariableAnalysis:
        context = self._read_module_fixture(module_name)
        module = context.source.module
        variable = module[name]

        assert isinstance(variable, Attribute)

        source_full_path = (
            context.project.project_root
            / context.project.source_root
            / context.source.path
        )
        source_lines = source_full_path.read_text(
            encoding="utf-8",
        ).splitlines()
        result = analyze_variable(
            variable=variable,
            name=name,
            source_lines=source_lines,
        )
        return result

    def _analyze_variable(self, name: str) -> VariableAnalysis:
        return self._analyze_variable_internal(
            name, PythonPath("analysis.symbol.types")
        )

    def _analyze_callable(self, name: str) -> VariableAnalysis:
        return self._analyze_variable_internal(
            name, PythonPath("analysis.symbol.callable")
        )

    def _analyze_generics(self, name: str) -> VariableAnalysis:
        return self._analyze_variable_internal(
            name, PythonPath("analysis.symbol.generics")
        )

    def test_analyze_type_int(self) -> None:
        result = self._analyze_variable("value_int")

        assert result.type is not None
        assert result.type.text == "int"
        assert isinstance(result.type.structure, NameStructureAnalysis)
        assert result.type.structure.name == "int"

    def test_analyze_type_str(self) -> None:
        result = self._analyze_variable("value_str")

        assert result.type is not None
        assert result.type.text == "str"
        assert isinstance(result.type.structure, NameStructureAnalysis)
        assert result.type.structure.name == "str"

    def test_analyze_type_none(self) -> None:
        result = self._analyze_variable("value_none")

        assert result.type is not None
        assert result.type.text == "None"
        assert isinstance(result.type.structure, NoneStructureAnalysis)

    def test_analyze_type_custom(self) -> None:
        result = self._analyze_variable("value_custom")

        assert result.type is not None
        assert result.type.text == "Foo"
        assert isinstance(result.type.structure, NameStructureAnalysis)
        assert result.type.structure.name == "Foo"

    def test_analyze_type_union(self) -> None:
        result = self._analyze_variable("value_union")

        assert result.type is not None
        assert result.type.text == "int | None | str | None"

        assert isinstance(result.type.structure, UnionStructureAnalysis)
        types = result.type.structure.types
        assert len(types) == 4

        assert isinstance(types[0], NameStructureAnalysis)
        assert types[0].name == "int"

        assert isinstance(types[1], NoneStructureAnalysis)

        assert isinstance(types[2], NameStructureAnalysis)
        assert types[2].name == "str"

        assert isinstance(types[3], NoneStructureAnalysis)
        # assert types[3].value == "None"

    def test_analyze_type_literal_int(self) -> None:
        result = self._analyze_variable("value_literal_int")

        assert result.type is not None
        assert result.type.text == "Literal[1]"

        assert isinstance(result.type.structure, LiteralStructureAnalysis)
        assert isinstance(result.type.structure.value, LiteralValue)
        assert result.type.structure.value.value == 1

    def test_analyze_type_literal_multiple_int(self) -> None:
        result = self._analyze_variable("value_literal_int2")

        assert result.type is not None
        assert isinstance(result.type.structure, LiteralStructureAnalysis)

        value = result.type.structure.value

        assert isinstance(value, TupleStructureAnalysis)
        assert len(value.elements) == 2

    def test_analyze_type_list(self) -> None:
        result = self._analyze_variable("value_list")

        assert result.type is not None
        assert result.type.text == "list[int]"

        assert isinstance(result.type.structure, ArrayStructureAnalysis)

        element = result.type.structure.element
        assert isinstance(element, NameStructureAnalysis)
        assert element.name == "int"

    def test_analyze_type_dict(self) -> None:
        result = self._analyze_variable("value_dict")

        assert result.type is not None
        assert result.type.text == "dict[str, int]"

        assert isinstance(result.type.structure, DictionaryStructureAnalysis)

        key = result.type.structure.keys
        value = result.type.structure.values

        assert isinstance(key, NameStructureAnalysis)
        assert key.name == "str"

        assert isinstance(value, NameStructureAnalysis)
        assert value.name == "int"

    def test_analyze_type_set(self) -> None:
        result = self._analyze_variable("value_set")

        assert result.type is not None
        assert result.type.text == "set[str]"

        assert isinstance(result.type.structure, SetStructureAnalysis)

        element = result.type.structure.element_type

        assert isinstance(element, NameStructureAnalysis)
        assert element.name == "str"

    def test_analyze_type_tuple(self) -> None:
        result = self._analyze_variable("value_tuple2")

        assert result.type is not None
        assert result.type.text == "tuple[str, int]"

        assert isinstance(result.type.structure, TupleStructureAnalysis)

        structure = result.type.structure

        assert structure.variable_length is False
        assert len(structure.elements) == 2

        assert isinstance(structure.elements[0], NameStructureAnalysis)
        assert structure.elements[0].name == "str"

        assert isinstance(structure.elements[1], NameStructureAnalysis)
        assert structure.elements[1].name == "int"

    def test_analyze_type_tuple_variable_length(self) -> None:
        result = self._analyze_variable("value_tuple")

        assert result.type is not None
        assert result.type.text == "tuple[str, ...]"

        assert isinstance(result.type.structure, TupleStructureAnalysis)

        structure = result.type.structure

        assert structure.variable_length is True
        assert len(structure.elements) == 1

        assert isinstance(structure.elements[0], NameStructureAnalysis)
        assert structure.elements[0].name == "str"

    def test_analyze_type_nested_tuple(self) -> None:
        result = self._analyze_variable("value_tuple_nested")

        assert result.type is not None
        assert isinstance(result.type.structure, TupleStructureAnalysis)

        outer = result.type.structure

        assert outer.variable_length is False
        assert len(outer.elements) == 2

        assert isinstance(outer.elements[0], NameStructureAnalysis)
        assert outer.elements[0].name == "str"

        assert isinstance(outer.elements[1], TupleStructureAnalysis)

        inner = outer.elements[1]

        assert inner.variable_length is False
        assert len(inner.elements) == 2

        assert isinstance(inner.elements[0], NameStructureAnalysis)
        assert inner.elements[0].name == "int"

        assert isinstance(inner.elements[1], NameStructureAnalysis)
        assert inner.elements[1].name == "bool"

    def test_analyze_type_nested_variable_length_tuple(self) -> None:
        result = self._analyze_variable("value_tuple_nested2")

        assert result.type is not None
        assert isinstance(result.type.structure, TupleStructureAnalysis)

        outer = result.type.structure

        assert outer.variable_length is False
        assert len(outer.elements) == 2

        assert isinstance(outer.elements[1], TupleStructureAnalysis)

        inner = outer.elements[1]

        assert inner.variable_length is True
        assert len(inner.elements) == 1

        assert isinstance(inner.elements[0], NameStructureAnalysis)
        assert inner.elements[0].name == "int"

    def test_analyze_type_nested_variable_length_tuple_2(self) -> None:
        result = self._analyze_variable("value_tuple_nested3")

        assert result.type is not None
        assert isinstance(result.type.structure, TupleStructureAnalysis)

        outer = result.type.structure

        assert outer.variable_length is True
        assert len(outer.elements) == 1

        assert isinstance(outer.elements[0], TupleStructureAnalysis)

        inner = outer.elements[0]

        assert inner.variable_length is True
        assert len(inner.elements) == 1

        assert isinstance(inner.elements[0], NameStructureAnalysis)
        assert inner.elements[0].name == "int"

    def test_analyze_type_callable(self) -> None:
        result = self._analyze_variable("value_callable")

        assert result.type is not None
        assert result.type.text == "Callable[[Exception], bool]"

        assert isinstance(result.type.structure, CallableStructureAnalysis)

        structure = result.type.structure

        assert structure.parameters is not None
        assert len(structure.parameters) == 1

        assert isinstance(structure.parameters[0], NameStructureAnalysis)
        assert structure.parameters[0].name == "Exception"

        assert isinstance(structure.return_type, NameStructureAnalysis)
        assert structure.return_type.name == "bool"

    def test_analyze_type_callable_with_multiple_parameters(self) -> None:
        result = self._analyze_variable("value_callable2")

        assert result.type is not None
        assert isinstance(result.type.structure, CallableStructureAnalysis)

        structure = result.type.structure

        assert structure.parameters is not None
        assert len(structure.parameters) == 3

        assert isinstance(structure.parameters[0], NameStructureAnalysis)
        assert structure.parameters[0].name == "str"

        assert isinstance(structure.parameters[1], NameStructureAnalysis)
        assert structure.parameters[1].name == "bool"

        assert isinstance(structure.parameters[2], DictionaryStructureAnalysis)

        assert isinstance(structure.return_type, ArrayStructureAnalysis)

    def test_analyze_callable_single_parameter(self) -> None:
        result = self._analyze_callable("value_callable_1")

        assert result.type is not None
        assert result.type.text == "Callable[[Exception], bool]"

        structure = result.type.structure
        assert isinstance(structure, CallableStructureAnalysis)

        assert structure.parameters is not None
        assert len(structure.parameters) == 1

        parameter = structure.parameters[0]
        assert isinstance(parameter, NameStructureAnalysis)
        assert parameter.name == "Exception"

        return_type = structure.return_type
        assert isinstance(return_type, NameStructureAnalysis)
        assert return_type.name == "bool"

    def test_analyze_callable_no_parameter(self) -> None:
        result = self._analyze_callable("value_callable_3")
        assert result.type is not None

        structure = result.type.structure
        assert isinstance(structure, CallableStructureAnalysis)
        assert structure.parameters == ()

    def test_analyze_callable_no_parameter_with_return(self) -> None:
        result = self._analyze_callable("value_callable_5")
        assert result.type is not None

        structure = result.type.structure
        assert isinstance(structure, CallableStructureAnalysis)
        assert structure.parameters == ()

        assert isinstance(
            structure.return_type,
            NoneStructureAnalysis,
        )

    def test_analyze_callable_variable_parameter(self) -> None:
        result = self._analyze_callable("value_callable_15")
        assert result.type is not None

        structure = result.type.structure
        assert isinstance(structure, CallableStructureAnalysis)
        assert structure.parameters is None

    def test_analyze_callable_7(self) -> None:
        result = self._analyze_callable("value_callable_7")

        assert result.type is not None
        assert result.type.text == "Callable[[str | None, int | float], bool]"

        structure = result.type.structure
        assert isinstance(structure, CallableStructureAnalysis)

        assert structure.parameters is not None
        assert len(structure.parameters) == 2

        first = structure.parameters[0]
        assert isinstance(first, UnionStructureAnalysis)
        assert len(first.types) == 2

        assert isinstance(first.types[0], NameStructureAnalysis)
        assert first.types[0].name == "str"

        assert isinstance(first.types[1], NoneStructureAnalysis)

        second = structure.parameters[1]
        assert isinstance(second, UnionStructureAnalysis)
        assert len(second.types) == 2

        assert isinstance(second.types[0], NameStructureAnalysis)
        assert second.types[0].name == "int"

        assert isinstance(second.types[1], NameStructureAnalysis)
        assert second.types[1].name == "float"

        assert isinstance(structure.return_type, NameStructureAnalysis)
        assert structure.return_type.name == "bool"

    def test_analyze_callable_8(self) -> None:
        result = self._analyze_callable("value_callable_8")

        assert result.type is not None
        assert result.type.text == "Callable[[str], str | None]"

        structure = result.type.structure
        assert isinstance(structure, CallableStructureAnalysis)

        assert structure.parameters is not None
        assert len(structure.parameters) == 1

        parameter = structure.parameters[0]
        assert isinstance(parameter, NameStructureAnalysis)
        assert parameter.name == "str"

        assert isinstance(structure.return_type, UnionStructureAnalysis)
        assert len(structure.return_type.types) == 2

        assert isinstance(structure.return_type.types[0], NameStructureAnalysis)
        assert structure.return_type.types[0].name == "str"

        assert isinstance(structure.return_type.types[1], NoneStructureAnalysis)

    def test_analyze_callable_9(self) -> None:
        result = self._analyze_callable("value_callable_9")

        assert result.type is not None
        assert result.type.text == "Callable[[Callable[[str], int]], bool]"

        structure = result.type.structure
        assert isinstance(structure, CallableStructureAnalysis)

        assert structure.parameters is not None
        assert len(structure.parameters) == 1

        parameter = structure.parameters[0]
        assert isinstance(parameter, CallableStructureAnalysis)

        assert parameter.parameters is not None
        assert len(parameter.parameters) == 1

        inner_parameter = parameter.parameters[0]
        assert isinstance(inner_parameter, NameStructureAnalysis)
        assert inner_parameter.name == "str"

        assert isinstance(parameter.return_type, NameStructureAnalysis)
        assert parameter.return_type.name == "int"

        assert isinstance(structure.return_type, NameStructureAnalysis)
        assert structure.return_type.name == "bool"

    def test_analyze_callable_10(self) -> None:
        result = self._analyze_callable("value_callable_10")

        assert result.type is not None
        assert result.type.text == "Callable[[str], Callable[[int], bool]]"

        structure = result.type.structure
        assert isinstance(structure, CallableStructureAnalysis)

        assert structure.parameters is not None
        assert len(structure.parameters) == 1

        parameter = structure.parameters[0]
        assert isinstance(parameter, NameStructureAnalysis)
        assert parameter.name == "str"

        return_type = structure.return_type
        assert isinstance(return_type, CallableStructureAnalysis)

        assert return_type.parameters is not None
        assert len(return_type.parameters) == 1

        inner_parameter = return_type.parameters[0]
        assert isinstance(inner_parameter, NameStructureAnalysis)
        assert inner_parameter.name == "int"

        assert isinstance(return_type.return_type, NameStructureAnalysis)
        assert return_type.return_type.name == "bool"

    def test_analyze_callable_11(self) -> None:
        result = self._analyze_callable("value_callable_11")

        assert result.type is not None
        assert result.type.text == (
            "Callable[[Callable[[str], int]], Callable[[bool], str]]"
        )

        structure = result.type.structure
        assert isinstance(structure, CallableStructureAnalysis)

        assert structure.parameters is not None
        assert len(structure.parameters) == 1

        parameter = structure.parameters[0]
        assert isinstance(parameter, CallableStructureAnalysis)

        assert parameter.parameters is not None
        assert len(parameter.parameters) == 1

        inner_parameter = parameter.parameters[0]
        assert isinstance(inner_parameter, NameStructureAnalysis)
        assert inner_parameter.name == "str"

        assert isinstance(parameter.return_type, NameStructureAnalysis)
        assert parameter.return_type.name == "int"

        return_type = structure.return_type
        assert isinstance(return_type, CallableStructureAnalysis)

        assert return_type.parameters is not None
        assert len(return_type.parameters) == 1

        inner_return_parameter = return_type.parameters[0]
        assert isinstance(inner_return_parameter, NameStructureAnalysis)
        assert inner_return_parameter.name == "bool"

        assert isinstance(return_type.return_type, NameStructureAnalysis)
        assert return_type.return_type.name == "str"

    def test_analyze_callable_12(self) -> None:
        result = self._analyze_callable("value_callable_12")

        assert result.type is not None
        assert result.type.text == "Callable[[tuple[str, int]], bool]"

        structure = result.type.structure
        assert isinstance(structure, CallableStructureAnalysis)

        assert structure.parameters is not None
        assert len(structure.parameters) == 1

        parameter = structure.parameters[0]
        assert isinstance(parameter, TupleStructureAnalysis)
        assert parameter.variable_length is False
        assert len(parameter.elements) == 2

        assert isinstance(parameter.elements[0], NameStructureAnalysis)
        assert parameter.elements[0].name == "str"

        assert isinstance(parameter.elements[1], NameStructureAnalysis)
        assert parameter.elements[1].name == "int"

        assert isinstance(structure.return_type, NameStructureAnalysis)
        assert structure.return_type.name == "bool"

    def test_analyze_callable_13(self) -> None:
        result = self._analyze_callable("value_callable_13")

        assert result.type is not None
        assert result.type.text == "Callable[[Literal['foo'], Literal[1]], bool]"

        structure = result.type.structure
        assert isinstance(structure, CallableStructureAnalysis)

        assert structure.parameters is not None
        assert len(structure.parameters) == 2

        first = structure.parameters[0]
        assert isinstance(first, LiteralStructureAnalysis)
        assert isinstance(first.value, LiteralValue)
        assert first.value.value == "foo"

        second = structure.parameters[1]
        assert isinstance(second, LiteralStructureAnalysis)
        assert isinstance(second.value, LiteralValue)
        assert second.value.value == 1

        assert isinstance(structure.return_type, NameStructureAnalysis)
        assert structure.return_type.name == "bool"

    def test_analyze_callable_14(self) -> None:
        result = self._analyze_callable("value_callable_14")

        assert result.type is not None
        assert result.type.text == "Callable[[str | None], None]"

        structure = result.type.structure
        assert isinstance(structure, CallableStructureAnalysis)

        assert structure.parameters is not None
        assert len(structure.parameters) == 1

        parameter = structure.parameters[0]
        assert isinstance(parameter, UnionStructureAnalysis)
        assert len(parameter.types) == 2

        assert isinstance(parameter.types[0], NameStructureAnalysis)
        assert parameter.types[0].name == "str"

        assert isinstance(parameter.types[1], NoneStructureAnalysis)

        assert isinstance(structure.return_type, NoneStructureAnalysis)

    def test_analyze_generic_simple(self) -> None:
        result = self._analyze_generics("value_generic_simple")

        assert result.type is not None
        assert result.type.text == "GenericClass[str]"

        structure = result.type.structure
        assert isinstance(structure, GenericsStructureAnalysis)

        assert isinstance(structure.base, NameStructureAnalysis)
        assert structure.base.name == "GenericClass"

        assert len(structure.parameters) == 1

        parameter = structure.parameters[0]
        assert isinstance(parameter, NameStructureAnalysis)
        assert parameter.name == "str"

    def test_analyze_generic_nested(self) -> None:
        result = self._analyze_generics("value_generic_nested")

        assert result.type is not None
        assert result.type.text == "GenericClass[list[str]]"

        structure = result.type.structure
        assert isinstance(structure, GenericsStructureAnalysis)

        assert isinstance(structure.base, NameStructureAnalysis)
        assert structure.base.name == "GenericClass"

        assert len(structure.parameters) == 1

        parameter = structure.parameters[0]
        assert isinstance(parameter, ArrayStructureAnalysis)

        assert isinstance(parameter.element, NameStructureAnalysis)
        assert parameter.element.name == "str"

    def test_analyze_generic_multiple(self) -> None:
        result = self._analyze_generics("value_generic_multiple")

        assert result.type is not None
        assert result.type.text == "GenericPair[str, int]"

        structure = result.type.structure
        assert isinstance(structure, GenericsStructureAnalysis)

        assert isinstance(structure.base, NameStructureAnalysis)
        assert structure.base.name == "GenericPair"

        assert len(structure.parameters) == 2

        first = structure.parameters[0]
        assert isinstance(first, NameStructureAnalysis)
        assert first.name == "str"

        second = structure.parameters[1]
        assert isinstance(second, NameStructureAnalysis)
        assert second.name == "int"

    def test_analyze_generic_deep_nested(self) -> None:
        result = self._analyze_generics("value_generic_deep_nested")

        assert result.type is not None
        assert result.type.text == "GenericClass[GenericPair[str, int]]"

        structure = result.type.structure
        assert isinstance(structure, GenericsStructureAnalysis)

        assert isinstance(structure.base, NameStructureAnalysis)
        assert structure.base.name == "GenericClass"

        assert len(structure.parameters) == 1

        parameter = structure.parameters[0]
        assert isinstance(parameter, GenericsStructureAnalysis)

        assert isinstance(parameter.base, NameStructureAnalysis)
        assert parameter.base.name == "GenericPair"

        assert len(parameter.parameters) == 2

        first = parameter.parameters[0]
        assert isinstance(first, NameStructureAnalysis)
        assert first.name == "str"

        second = parameter.parameters[1]
        assert isinstance(second, NameStructureAnalysis)
        assert second.name == "int"

    # def test_analyzes_variable_with_type_annotation(self) -> None:
    #     result = self._analyze_variable(
    #         "value_int",
    #     )

    #     # assert result.type is not None
    #     # assert result.type.text == "int"

    #     result = self._analyze_variable(
    #         "value_str",
    #     )

    #     result = self._analyze_variable(
    #         "value_none",
    #     )
    #     result = self._analyze_variable(
    #         "value_custom",
    #     )
    #     result = self._analyze_variable(
    #         "value_list",
    #     )
    #     result = self._analyze_variable(
    #         "value_union",
    #     )
    #     result = self._analyze_variable(
    #         "value_dict",
    #     )
    #     result = self._analyze_variable(
    #         "value_tuple",
    #     )
    #     result = self._analyze_variable(
    #         "value_literal_int",
    #     )
    #     result = self._analyze_variable(
    #         "value_literal_int2",
    #     )
    #     result = self._analyze_variable(
    #         "value_literal_str",
    #     )
    #     result = self._analyze_variable(
    #         "value_literal_str2",
    #     )
    #     result = self._analyze_variable(
    #         "value_literal_bool",
    #     )
    #     result = self._analyze_variable(
    #         "value_literal_bool2",
    #     )
    #     result = self._analyze_variable(
    #         "value_callable",
    #     )
    #     result = self._analyze_variable(
    #         "value_callable2",
    #     )

    #     result = self._analyze_variable("value_tuple2")
    #     result = self._analyze_variable("value_tuple_nested")
    #     result = self._analyze_variable("value_tuple_nested2")
    #     result = self._analyze_variable("value_tuple_empty")
    #     result = self._analyze_variable("value_tuple_nested3")
    #     # print(result)
    #     result = self._analyze_variable("value_set")
    #     result = self._analyze_variable("value_set_nested")

    # @pytest.mark.parametrize(
    #     ("name"),
    #     [
    #         ("value_callable_1"),
    #         ("value_callable_2"),
    #         ("value_callable_3"),
    #         ("value_callable_4"),
    #         ("value_callable_5"),
    #         ("value_callable_6"),
    #         ("value_callable_7"),
    #         ("value_callable_8"),
    #         ("value_callable_9"),
    #         ("value_callable_10"),
    #         ("value_callable_11"),
    #         ("value_callable_12"),
    #         ("value_callable_13"),
    #         ("value_callable_14"),
    #         ("value_callable_15"),
    #     ],
    # )
    # def test_analyzes_variable_with_callable(
    #     self,
    #     name: str,
    # ) -> None:
    #     self._analyze_callable(name)

    # @pytest.mark.parametrize(
    #     ("name"),
    #     [
    #         ("value_generic_simple"),
    #         ("value_generic_nested"),
    #         ("value_generic_multiple"),
    #         ("value_generic_deep_nested"),
    #     ],
    # )
    # def test_analyzes_variable_with_generics(
    #     self,
    #     name: str,
    # ) -> None:
    #     result = self._analyze_generics(name)
    #     print(result)
