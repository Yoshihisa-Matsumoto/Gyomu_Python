from gyomu_schema.schemas.document.document import Document
from gyomu_schema.utility.serialization import _assert_json_round_trip

from packages.schema.schema_test_support.concept_helpers import create_document


class TestDocument:
    def test(self) -> None:
        _assert_json_round_trip(Document, create_document())
