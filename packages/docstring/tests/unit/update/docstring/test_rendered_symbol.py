from gyomu_docstring.update.docstring.rendered_symbol import RenderedSymbolDocstring
from gyomu_schema.utility.serialization import _assert_json_round_trip

from packages.schema.schema_test_support.helpers import (
    create_declaration_identity,
    create_location,
)


class TestRenderedSymbolDocstring:
    def test(self) -> None:
        _assert_json_round_trip(
            RenderedSymbolDocstring,
            RenderedSymbolDocstring(
                identity=create_declaration_identity("ID1"),
                docstring="ABCDE",
                location=create_location(),
            ),
        )
