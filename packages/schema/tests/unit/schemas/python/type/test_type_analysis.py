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

from packages.schema.schema_test_support.helpers import (
    create_array_structure,
    create_attribute_structure,
    create_call_structure,
    create_callable_structure,
    create_dictionary_structure,
    create_generics_structure,
    create_keyword_structure,
    create_literal_structure,
    create_name_structure,
    create_set_structure,
    create_tuple_structure,
    create_type_analysis,
    create_union_structure,
)


class TestTypeAnalysis:
    def test(self) -> None:
        _assert_json_round_trip(
            TypeAnalysis,
            create_type_analysis(
                text="int", structure=create_name_structure(name="ABC")
            ),
        )


class TestUnionStructureAnalysis:
    def test(self) -> None:
        _assert_json_round_trip(
            UnionStructureAnalysis,
            create_union_structure(
                types=(
                    create_name_structure(name="ABC"),
                    create_name_structure(name="DEF"),
                )
            ),
        )


class TestAttributeStructureAnalysis:
    def test(self) -> None:
        _assert_json_round_trip(
            AttributeStructureAnalysis,
            create_attribute_structure(
                values=(
                    create_name_structure(name="ABC"),
                    create_name_structure(name="DEF"),
                )
            ),
        )


class TestTupleStructureAnalysis:
    def test(self) -> None:
        _assert_json_round_trip(
            TupleStructureAnalysis,
            create_tuple_structure(
                elements=[
                    create_name_structure(name="ABC"),
                ]
            ),
        )


class TestSetStructureAnalysis:
    def test(self) -> None:
        _assert_json_round_trip(
            SetStructureAnalysis,
            create_set_structure(element_type=create_name_structure(name="ABC")),
        )


class TestLiteralStructureAnalysis:
    def test(self) -> None:
        _assert_json_round_trip(
            LiteralStructureAnalysis,
            create_literal_structure(value=create_name_structure(name="ABC")),
        )


class TestArrayStructureAnalysis:
    def test(self) -> None:
        _assert_json_round_trip(
            ArrayStructureAnalysis,
            create_array_structure(element=create_name_structure(name="ABC")),
        )


class TestDictionaryStructureAnalysis:
    def test(self) -> None:
        _assert_json_round_trip(
            DictionaryStructureAnalysis,
            create_dictionary_structure(
                keys=create_name_structure(name="ABC"),
                values=create_name_structure(name="DEF"),
            ),
        )


class TestCallableStructureAnalysis:
    def test(self) -> None:
        _assert_json_round_trip(
            CallableStructureAnalysis,
            create_callable_structure(
                return_type=create_name_structure(name="ABC"),
                parameters=(create_name_structure(name="DEF"),),
            ),
        )


class TestCallStructureAnalysis:
    def test(self) -> None:
        _assert_json_round_trip(
            CallStructureAnalysis,
            create_call_structure(
                function=create_name_structure(name="ABC"),
                arguments=(create_name_structure(name="DEF"),),
            ),
        )


class TestGenericsStructureAnalysis:
    def test(self) -> None:
        _assert_json_round_trip(
            GenericsStructureAnalysis,
            create_generics_structure(
                base=create_name_structure(name="ABC"),
                parameters=(create_name_structure(name="DEF"),),
            ),
        )


class TestKeywordStructureAnalysis:
    def test(self) -> None:
        _assert_json_round_trip(
            KeywordStructureAnalysis,
            create_keyword_structure(
                name="name1",
                value=create_name_structure(name="ABC"),
            ),
        )
