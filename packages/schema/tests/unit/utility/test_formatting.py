from dataclasses import dataclass

from gyomu_schema.utility.fromatting import format_object


@dataclass
class Sample:
    name: str
    value: int


def test_format_object_with_dataclass() -> None:
    value = Sample(name="test", value=123)

    result = format_object(value)

    assert result == "{'name': 'test', 'value': 123}"


def test_format_object_with_object() -> None:
    class Sample:
        def __init__(self) -> None:
            self.name = "test"
            self.value = 123

    value = Sample()

    result = format_object(value)

    assert result == "{'name': 'test', 'value': 123}"


def test_format_object_with_value_without_dict() -> None:
    result = format_object(123)

    assert result == "123"


def test_format_object_with_dataclass_type() -> None:
    result = format_object(Sample)

    assert "Sample" in result
