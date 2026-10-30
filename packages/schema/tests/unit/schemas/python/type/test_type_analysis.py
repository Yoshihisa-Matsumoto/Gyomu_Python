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
    TupleStructureAnalysis,
    TypeAnalysis,
    UnionStructureAnalysis,
)
from gyomu_schema.utility.serialization import _assert_json_round_trip

from packages.schema.test_support.helpers import (
    create_array_structure_analysis,
    create_attribute_structure_analysis,
    create_call_structure_analysis,
    create_callable_structure_analysis,
    create_dictionary_structure_analysis,
    create_generics_structure_analysis,
    create_keyword_structure_analysis,
    create_literal_structure_analysis,
    create_name_structure_analysis,
    create_set_structure_analysis,
    create_tuple_structure_analysis,
    create_type_analysis,
    create_union_structure_analysis,
)


class TestTypeAnalysis:
    def test(self) -> None:
        _assert_json_round_trip(
            TypeAnalysis,
            create_type_analysis(
                text="int", structure=create_name_structure_analysis(name="ABC")
            ),
        )


class TestUnionStructureAnalysis:
    def test(self) -> None:
        _assert_json_round_trip(
            UnionStructureAnalysis,
            create_union_structure_analysis(
                types=(
                    create_name_structure_analysis(name="ABC"),
                    create_name_structure_analysis(name="DEF"),
                )
            ),
        )


class TestAttributeStructureAnalysis:
    def test(self) -> None:
        _assert_json_round_trip(
            AttributeStructureAnalysis,
            create_attribute_structure_analysis(
                values=(
                    create_name_structure_analysis(name="ABC"),
                    create_name_structure_analysis(name="DEF"),
                )
            ),
        )


class TestTupleStructureAnalysis:
    def test(self) -> None:
        _assert_json_round_trip(
            TupleStructureAnalysis,
            create_tuple_structure_analysis(
                elements=[
                    create_name_structure_analysis(name="ABC"),
                ]
            ),
        )


class TestSetStructureAnalysis:
    def test(self) -> None:
        _assert_json_round_trip(
            SetStructureAnalysis,
            create_set_structure_analysis(
                element_type=create_name_structure_analysis(name="ABC")
            ),
        )


class TestLiteralStructureAnalysis:
    def test(self) -> None:
        _assert_json_round_trip(
            LiteralStructureAnalysis,
            create_literal_structure_analysis(
                value=create_name_structure_analysis(name="ABC")
            ),
        )


class TestArrayStructureAnalysis:
    def test(self) -> None:
        _assert_json_round_trip(
            ArrayStructureAnalysis,
            create_array_structure_analysis(
                element=create_name_structure_analysis(name="ABC")
            ),
        )


class TestDictionaryStructureAnalysis:
    def test(self) -> None:
        _assert_json_round_trip(
            DictionaryStructureAnalysis,
            create_dictionary_structure_analysis(
                keys=create_name_structure_analysis(name="ABC"),
                values=create_name_structure_analysis(name="DEF"),
            ),
        )


class TestCallableStructureAnalysis:
    def test(self) -> None:
        _assert_json_round_trip(
            CallableStructureAnalysis,
            create_callable_structure_analysis(
                return_type=create_name_structure_analysis(name="ABC"),
                parameters=(create_name_structure_analysis(name="DEF"),),
            ),
        )


class TestCallStructureAnalysis:
    def test(self) -> None:
        _assert_json_round_trip(
            CallStructureAnalysis,
            create_call_structure_analysis(
                function=create_name_structure_analysis(name="ABC"),
                arguments=(create_name_structure_analysis(name="DEF"),),
            ),
        )


class TestGenericsStructureAnalysis:
    def test(self) -> None:
        _assert_json_round_trip(
            GenericsStructureAnalysis,
            create_generics_structure_analysis(
                base=create_name_structure_analysis(name="ABC"),
                parameters=(create_name_structure_analysis(name="DEF"),),
            ),
        )


class TestKeywordStructureAnalysis:
    def test(self) -> None:
        _assert_json_round_trip(
            KeywordStructureAnalysis,
            create_keyword_structure_analysis(
                name="name1",
                value=create_name_structure_analysis(name="ABC"),
            ),
        )
