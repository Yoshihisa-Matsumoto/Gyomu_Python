from gyomu_docstring.update.docstring.line import (
    DocstringBlank,
    DocstringSectionItem,
    DocstringText,
)
from gyomu_schema.utility.serialization import _assert_json_round_trip


class TestDocstringText:
    def test(self) -> None:
        _assert_json_round_trip(DocstringText, DocstringText(text="ABCDEFG!!"))


class TestDocstringBlank:
    def test(self) -> None:
        _assert_json_round_trip(DocstringBlank, DocstringBlank())


class TestDocstringSectionItem:
    def test(self) -> None:
        _assert_json_round_trip(
            DocstringSectionItem, DocstringSectionItem(text="ABCDEFG!!")
        )
