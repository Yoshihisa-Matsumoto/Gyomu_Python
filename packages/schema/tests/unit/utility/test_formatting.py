from ast import literal_eval
from dataclasses import dataclass

from gyomu_schema.utility.fromatting import format_object
from pydantic import BaseModel


@dataclass
class Sample:
    name: str
    value: int


@dataclass
class NestedDataclass:
    name: str
    child: Sample


class NestedObject:
    def __init__(self, name: str, child: object) -> None:
        self.name = name
        self.child = child


class SampleModel(BaseModel):
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


def test_format_object_with_nested_dataclass() -> None:
    value = NestedDataclass(
        name="parent",
        child=Sample(name="child", value=123),
    )

    result = format_object(value)

    assert "'name': 'parent'" in result
    assert "'child': {'name': 'child', 'value': 123}" in result


def test_format_object_with_nested_object() -> None:
    value = NestedObject(
        name="parent",
        child=NestedObject(name="child", child=123),
    )

    result = literal_eval(format_object(value))

    assert result == {
        "name": "parent",
        "child": {
            "name": "child",
            "child": 123,
        },
    }


def test_format_object_with_nested_base_model() -> None:
    value = NestedObject(
        name="parent",
        child=SampleModel(name="child", value=123),
    )

    result = literal_eval(format_object(value))

    assert result == {
        "name": "parent",
        "child": {
            "name": "child",
            "value": 123,
        },
    }


def test_format_object_with_nested_mixed_objects() -> None:
    value = NestedDataclass(
        name="parent",
        child=Sample(
            name="child",
            value=123,
        ),
    )

    result = literal_eval(format_object(value))

    assert result == {
        "name": "parent",
        "child": {
            "name": "child",
            "value": 123,
        },
    }


def test_format_object_with_depth() -> None:
    value = NestedObject(
        name="level1",
        child=NestedObject(
            name="level2",
            child=NestedObject(
                name="level3",
                child=123,
            ),
        ),
    )

    result = literal_eval(format_object(value, depth=2))

    assert result == {
        "name": "level1",
        "child": {
            "name": "level2",
            "child": "<NestedObject ...>",
        },
    }
