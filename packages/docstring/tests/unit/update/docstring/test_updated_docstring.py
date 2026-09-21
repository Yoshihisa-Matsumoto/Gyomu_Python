from gyomu_docstring.update.docstring.updated_docstring import UpdatedDocstring
from gyomu_schema.utility.serialization import _assert_json_round_trip

from packages.schema.schema_test_support.helpers import (
    create_declaration_identity,
    create_docstring,
)


class TestUpdatedDocstring:
    def test(self) -> None:
        _assert_json_round_trip(
            UpdatedDocstring,
            UpdatedDocstring(
                identity=create_declaration_identity("ID1"),
                docstring=create_docstring(summary="ABCDE##FA"),
            ),
        )
