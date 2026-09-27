from gyomu_schema.schemas.python.type.expression import (
    KeywordAnalysis,
    NameExpressionAnalysis,
)
from gyomu_schema.schemas.python.type.structure import LiteralValue
from gyomu_schema.utility.serialization import _assert_json_round_trip


class TestKeywordAnalysis:
    def test(self) -> None:
        _assert_json_round_trip(
            KeywordAnalysis,
            KeywordAnalysis(arg="A", value=LiteralValue(value=1)),
        )


class TestNameExpressionAnalysis:
    def test(self) -> None:
        _assert_json_round_trip(
            NameExpressionAnalysis,
            NameExpressionAnalysis(name="ABCE"),
        )
