from gyomu_ai_compiler.pipelines.docstring_update.schema.ai_plan import (
    DescriptionPlan,
    DocstringUpdateEntry,
    DocstringUpdatePlan,
    ParamActionValue,
    ParamUpdateAction,
    ParamUpdatePlan,
    ParamUpdateReplaceAction,
    RaiseActionValue,
    RaiseUpdateAction,
    RaiseUpdatePlan,
    RaiseUpdateReplaceAction,
    Reasoning,
    ReturnActionValue,
    ReturnUpdateAction,
    ReturnUpdatePlan,
    ReturnUpdateReplaceAction,
    Risk,
    SummaryPlan,
    UpdateAction,
    UpdateDeleteAction,
    UpdatePreserveAction,
    UpdateReplaceAction,
)
from gyomu_schema.utility.serialization import _assert_json_round_trip
from pydantic import TypeAdapter

from packages.schema.schema_test_support.helpers import create_declaration_identity


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


class TestUpdateReplaceAction:
    def test(self) -> None:
        _assert_json_round_trip(
            UpdateReplaceAction,
            UpdateReplaceAction(value="ABC#"),
        )


class TestUpdatePreserveAction:
    def test(self) -> None:
        _assert_json_round_trip(
            UpdatePreserveAction,
            UpdatePreserveAction(),
        )


class TestUpdateDeleteAction:
    def test(self) -> None:
        _assert_json_round_trip(
            UpdateDeleteAction,
            UpdateDeleteAction(),
        )


class TestSummaryPlan:
    def test(self) -> None:
        _assert_json_round_trip(
            SummaryPlan,
            SummaryPlan(action=UpdatePreserveAction(), confidence=1.0),
        )


class TestDescriptionPlan:
    def test(self) -> None:
        _assert_json_round_trip(
            DescriptionPlan,
            DescriptionPlan(action=UpdatePreserveAction(), confidence=1.0),
        )


class TestParamActionValue:
    def test(self) -> None:
        _assert_json_round_trip(
            ParamActionValue,
            ParamActionValue(type="ACB", description="CKDDF###F"),
        )


class TestParamUpdateReplaceAction:
    def test(self) -> None:
        _assert_json_round_trip(
            ParamUpdateReplaceAction,
            ParamUpdateReplaceAction(
                value=ParamActionValue(type="ACB", description="ADRF")
            ),
        )


class TestParamUpdatePlan:
    def test(self) -> None:
        _assert_json_round_trip(
            ParamUpdatePlan,
            ParamUpdatePlan(
                name="ABC", sort_order=1, action=UpdatePreserveAction(), confidence=0
            ),
        )


class TestRaiseActionValue:
    def test(self) -> None:
        _assert_json_round_trip(
            RaiseActionValue,
            RaiseActionValue(error_type="ACD#", description="DKFDF#"),
        )


class TestRaiseUpdateReplaceAction:
    def test(self) -> None:
        _assert_json_round_trip(
            RaiseUpdateReplaceAction,
            RaiseUpdateReplaceAction(
                value=RaiseActionValue(error_type="ABC", description="DFADF")
            ),
        )


class TestRaiseUpdatePlan:
    def test(self) -> None:
        _assert_json_round_trip(
            RaiseUpdatePlan,
            RaiseUpdatePlan(
                action=UpdatePreserveAction(),
                confidence=1.0,
                error_type="ABC",
            ),
        )


class TestReturnActionValue:
    def test(self) -> None:
        _assert_json_round_trip(
            ReturnActionValue,
            ReturnActionValue(return_type="ABC", description="DFDF"),
        )


class TestReturnUpdateReplaceAction:
    def test(self) -> None:
        _assert_json_round_trip(
            ReturnUpdateReplaceAction,
            ReturnUpdateReplaceAction(
                value=ReturnActionValue(return_type="ABC", description="DFDF")
            ),
        )


class TestReturnUpdatePlan:
    def test(self) -> None:
        _assert_json_round_trip(
            ReturnUpdatePlan,
            ReturnUpdatePlan(
                action=ReturnUpdateReplaceAction(
                    value=ReturnActionValue(return_type="ABC", description="DFDF")
                ),
                confidence=0,
            ),
        )


class TestReasoning:
    def test(self) -> None:
        _assert_json_round_trip(
            Reasoning,
            Reasoning(
                summary="SUMMARY", param_mapping="AFDGDF", return_mapping="ADFAF##"
            ),
        )


class TestRisk:
    def test(self) -> None:
        _assert_json_round_trip(
            Risk,
            Risk(has_human_conflict=True, risk_level="high"),
        )


class TestDocstringUpdateEntry:
    def test(self) -> None:
        _assert_json_round_trip(
            DocstringUpdateEntry,
            DocstringUpdateEntry(
                identity=create_declaration_identity("ID1"),
                summary=SummaryPlan(action=UpdatePreserveAction(), confidence=0),
                description=DescriptionPlan(
                    action=UpdatePreserveAction(), confidence=0
                ),
                params=(
                    ParamUpdatePlan(
                        name="ABC",
                        sort_order=1,
                        action=UpdatePreserveAction(),
                        confidence=0,
                    ),
                ),
                raises=(
                    RaiseUpdatePlan(
                        action=UpdatePreserveAction(),
                        confidence=1.0,
                        error_type="ABC",
                    ),
                ),
                returns=ReturnUpdatePlan(
                    action=ReturnUpdateReplaceAction(
                        value=ReturnActionValue(return_type="ABC", description="DFDF")
                    ),
                    confidence=0,
                ),
                reasoning=Reasoning(
                    summary="SUMMARY", param_mapping="AFDGDF", return_mapping="ADFAF##"
                ),
                risk=Risk(has_human_conflict=True, risk_level="high"),
            ),
        )


class TestDocstringUpdatePlan:
    def test(self) -> None:
        _assert_json_round_trip(
            DocstringUpdatePlan,
            DocstringUpdatePlan(
                entries=(
                    DocstringUpdateEntry(
                        identity=create_declaration_identity("ID1"),
                        summary=SummaryPlan(
                            action=UpdatePreserveAction(), confidence=0
                        ),
                        description=DescriptionPlan(
                            action=UpdatePreserveAction(), confidence=0
                        ),
                        params=(
                            ParamUpdatePlan(
                                name="ABC",
                                sort_order=1,
                                action=UpdatePreserveAction(),
                                confidence=0,
                            ),
                        ),
                        raises=(
                            RaiseUpdatePlan(
                                action=UpdatePreserveAction(),
                                confidence=1.0,
                                error_type="ABC",
                            ),
                        ),
                        returns=ReturnUpdatePlan(
                            action=ReturnUpdateReplaceAction(
                                value=ReturnActionValue(
                                    return_type="ABC", description="DFDF"
                                )
                            ),
                            confidence=0,
                        ),
                        reasoning=Reasoning(
                            summary="SUMMARY",
                            param_mapping="AFDGDF",
                            return_mapping="ADFAF##",
                        ),
                        risk=Risk(has_human_conflict=True, risk_level="high"),
                    ),
                ),
            ),
        )
