from gyomu_ai_compiler.pipelines.docstring_update.schema.ai_plan import (
    DocstringUpdateEntry,
    DocstringUpdatePlan,
    ParamActionValue,
    ParamUpdateAction,
    ParamUpdatePlan,
    RaiseUpdateAction,
    ReturnUpdateAction,
    UpdateAction,
    UpdateReplaceAction,
)
from pydantic import TypeAdapter


def test_replace_action_json_schema() -> None:
    schema = UpdateReplaceAction.model_json_schema()

    assert "Replace" in schema["description"]

    assert schema["properties"]["type"]["const"] == "replace"
    assert schema["properties"]["type"]["default"] == "replace"

    assert schema["properties"]["value"]["type"] == "string"
    assert schema["required"] == ["value"]


def test_merge_action_json_schema() -> None:
    schema = TypeAdapter(UpdateAction).json_schema()

    assert "Deterministic Docstring update action" in schema["description"]

    assert schema["discriminator"]["propertyName"] == "type"
    assert set(schema["discriminator"]["mapping"]) == {
        "replace",
        "preserve",
        "delete",
    }

    assert len(schema["oneOf"]) == 3


def test_param_merge_action_json_schema() -> None:
    schema = TypeAdapter(ParamUpdateAction).json_schema()

    assert "Deterministic Docstring update action" in schema["description"]

    assert schema["discriminator"]["propertyName"] == "type"
    assert set(schema["discriminator"]["mapping"]) == {
        "replace",
        "preserve",
        "delete",
    }

    assert len(schema["oneOf"]) == 3


def test_raise_merge_action_json_schema() -> None:
    schema = TypeAdapter(RaiseUpdateAction).json_schema()

    assert schema["discriminator"]["propertyName"] == "type"
    assert set(schema["discriminator"]["mapping"]) == {
        "replace",
        "preserve",
        "delete",
    }


def test_return_merge_action_json_schema() -> None:
    schema = TypeAdapter(ReturnUpdateAction).json_schema()

    assert schema["discriminator"]["propertyName"] == "type"
    assert set(schema["discriminator"]["mapping"]) == {
        "replace",
        "preserve",
        "delete",
    }


def test_param_plan_json_schema() -> None:
    schema = ParamUpdatePlan.model_json_schema()

    assert "Parameter update plan" in schema["description"]

    properties = schema["properties"]

    assert properties["name"]["type"] == "string"
    assert "Parameter name from function signature" in properties["name"]["description"]

    assert properties["sort_order"]["type"] == "integer"
    assert (
        "Parameter position in the function signature"
        in (properties["sort_order"]["description"])
    )

    assert "action" in properties
    assert "confidence" in properties

    assert schema["required"] == [
        "name",
        "sort_order",
        "action",
        "confidence",
    ]


def test_param_action_value_json_schema() -> None:
    schema = ParamActionValue.model_json_schema()

    assert schema["properties"]["type"]["anyOf"] == [
        {"type": "string"},
        {"type": "null"},
    ]

    assert (
        "Complete replacement parameter metadata"
        in (schema["properties"]["description"]["description"])
    )


def test_docstring_update_entry_json_schema() -> None:
    schema = DocstringUpdateEntry.model_json_schema()

    assert "AI-generated structured plan" in schema["description"]

    properties = schema["properties"]

    assert {
        "identity",
        "summary",
        "description",
        "params",
        "raises",
        "returns",
        "reasoning",
        "risk",
    } <= properties.keys()

    assert set(schema["required"]) == {
        "identity",
        "summary",
        "description",
        "params",
        "raises",
        "returns",
        "reasoning",
        "risk",
    }


def test_docstring_update_plan_json_schema() -> None:
    schema = DocstringUpdatePlan.model_json_schema()

    assert "Collection of Docstring update plans" in schema["description"]

    assert "entries" in schema["properties"]
    assert schema["properties"]["entries"]["type"] == "array"
    assert schema["required"] == ["entries"]
