from gyomu_schema.schemas.confidence import Confidence
from pydantic import TypeAdapter


def test_confidence_json_schema() -> None:
    schema = TypeAdapter(Confidence).json_schema()

    assert schema["type"] == "number"
    assert schema["minimum"] == 0.0
    assert schema["maximum"] == 1.0

    assert "description" in schema
    assert "AI decision confidence" in schema["description"]
