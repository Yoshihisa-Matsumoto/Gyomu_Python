from gyomu_schema.schemas.config.test.model_defaults import (
    AttributeParameter,
    CallParameter,
    DictEntry,
    DictParameter,
    KeywordArgument,
    ListParameter,
    LiteralParameter,
    ModelDefault,
    ModelDefaults,
    NoneParameter,
    ParameterDefault,
    TupleParameter,
)
from gyomu_schema.utility.serialization import _assert_json_round_trip

from packages.schema.test_support.helpers import (
    create_attribute_parameter,
    create_call_parameter,
    create_dict_entry,
    create_dict_parameter,
    create_keyword_argument,
    create_list_parameter,
    create_literal_parameter,
    create_model_default,
    create_model_defaults,
    create_none_parameter,
    create_parameter_default,
    create_tuple_parameter,
)


class TestLiteralExpression:
    def test(self) -> None:
        _assert_json_round_trip(
            LiteralParameter,
            create_literal_parameter(),
        )


class TestNoneExpression:
    def test(self) -> None:
        _assert_json_round_trip(
            NoneParameter,
            create_none_parameter(),
        )


class TestEnumExpression:
    def test(self) -> None:
        _assert_json_round_trip(
            AttributeParameter,
            create_attribute_parameter(),
        )


class TestTupleExpression:
    def test(self) -> None:
        _assert_json_round_trip(
            TupleParameter,
            create_tuple_parameter(),
        )


class TestListExpression:
    def test(self) -> None:
        _assert_json_round_trip(
            ListParameter,
            create_list_parameter(),
        )


class TestDictEntry:
    def test(self) -> None:
        _assert_json_round_trip(
            DictEntry,
            create_dict_entry(),
        )


class TestDictParameter:
    def test(self) -> None:
        _assert_json_round_trip(
            DictParameter,
            create_dict_parameter(),
        )


class TestKeywordArgument:
    def test(self) -> None:
        _assert_json_round_trip(
            KeywordArgument,
            create_keyword_argument(),
        )


class TestCallParameter:
    def test(self) -> None:
        _assert_json_round_trip(
            CallParameter,
            create_call_parameter(),
        )


class TestParameterDefault:
    def test(self) -> None:
        _assert_json_round_trip(
            ParameterDefault,
            create_parameter_default(),
        )


class TestModelDefault:
    def test(self) -> None:
        _assert_json_round_trip(
            ModelDefault,
            create_model_default(),
        )


class TestModelDefaults:
    def test(self) -> None:
        _assert_json_round_trip(
            ModelDefaults,
            create_model_defaults(),
        )
