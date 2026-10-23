from gyomu_schema.schemas.config.test.model_defaults import (
    EnumParameter,
    ListParameter,
    LiteralParameter,
    NoneParameter,
    TupleParameter,
)
from gyomu_schema.utility.serialization import _assert_json_round_trip

from packages.schema.test_support.helpers import create_declaration_identity


class TestLiteralExpression:
    def test(self) -> None:
        _assert_json_round_trip(
            LiteralParameter,
            LiteralParameter(value=1),
        )


class TestNoneExpression:
    def test(self) -> None:
        _assert_json_round_trip(
            NoneParameter,
            NoneParameter(),
        )


class TestEnumExpression:
    def test(self) -> None:
        _assert_json_round_trip(
            EnumParameter,
            EnumParameter(
                enum_identity=create_declaration_identity("test"), member_name="ABC"
            ),
        )


class TestTupleExpression:
    def test(self) -> None:
        _assert_json_round_trip(
            TupleParameter,
            TupleParameter(elements=(NoneParameter(),)),
        )


class TestListExpression:
    def test(self) -> None:
        _assert_json_round_trip(
            ListParameter,
            ListParameter(elements=(NoneParameter(),)),
        )


class TestDictEntry:
    def test(self) -> None:
        _assert_json_round_trip(
            ListParameter,
            ListParameter(elements=(NoneParameter(),)),
        )
