from gyomu_docstring.update.docstring.updated_docstring import UpdatedDocstring
from gyomu_schema.utility.serialization import _assert_json_round_trip

from packages.schema.test_support.helpers import (
    create_docstring,
    simple_create_declaration_identity,
)


class TestUpdatedDocstring:
    def test(self) -> None:
        _assert_json_round_trip(
            UpdatedDocstring,
            UpdatedDocstring(
                identity=simple_create_declaration_identity("ID1"),
                docstring=create_docstring(summary="ABCDE##FA"),
            ),
        )
