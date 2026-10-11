import json

from gyomu_ai_compiler.pipelines.llm_context.renderer.editing_rule import (
    build_editing_rule_messages,
)
from gyomu_schema.error.io import GyomuIOError, IOLayer, IOOperation
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.schema.schema_test_support.concept_helpers import (
    create_coding_guideline,
    create_coding_rule,
    create_llm_context_build_context,
    create_llm_knowledge,
)


class TestBuildEditingRuleMessages:
    def test_builds_messages(
        self,
        mocker: MockerFixture,
    ) -> None:
        context = create_llm_context_build_context(
            knowledge=create_llm_knowledge(
                coding_guideline=create_coding_guideline(
                    rules=(
                        create_coding_rule(
                            category="Category 1",
                            rule="Rule 1",
                            rationale="Rationale 1",
                        ),
                        create_coding_rule(
                            category="Category 2",
                            rule="Rule 2",
                            rationale=None,
                        ),
                    ),
                    forbidden=(
                        "Forbidden 1",
                        "Forbidden 2",
                    ),
                ),
            ),
        )

        load_prompt = mocker.patch(
            "gyomu_ai_compiler.pipelines.llm_context.renderer.editing_rule.load_prompt",
            return_value=Success("editing rule prompt"),
        )

        result = build_editing_rule_messages(context)

        assert isinstance(result, Success)

        conversation = result.unwrap()

        assert conversation.system
        assert conversation.system.parts[0].text == "editing rule prompt"

        assert conversation.request
        assert len(conversation.request.parts) == 1
        assert conversation.request.parts[0] is not None

        msg = conversation.request.parts[0].text
        user_data = json.loads(msg)

        assert user_data == {
            "rules": [
                {
                    "category": "Category 1",
                    "rule": "Rule 1",
                    "rationale": "Rationale 1",
                },
                {
                    "category": "Category 2",
                    "rule": "Rule 2",
                    "rationale": None,
                },
            ],
            "forbidden": [
                "Forbidden 1",
                "Forbidden 2",
            ],
        }

        load_prompt.assert_called_once_with(
            name="llm_context/editing-rule.md",
        )

    def test_propagates_prompt_load_failure(
        self,
        mocker: MockerFixture,
    ) -> None:
        error = GyomuIOError(
            "failed to load prompt",
            layer=IOLayer.FILESYSTEM,
            operation=IOOperation.READ,
        )

        mocker.patch(
            "gyomu_ai_compiler.pipelines.llm_context.renderer.editing_rule.load_prompt",
            return_value=Failure(error),
        )

        result = build_editing_rule_messages(
            create_llm_context_build_context(),
        )

        assert result == Failure(error)
