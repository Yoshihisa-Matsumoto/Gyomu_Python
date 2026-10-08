import json

from gyomu_ai_compiler.pipelines.llm_context.renderer.design_principles import (
    build_design_principles_messages,
)
from gyomu_schema.error.io import GyomuIOError, IOLayer, IOOperation
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.schema.schema_test_support.concept_helpers import (
    create_llm_context_build_context,
    create_llm_knowledge,
    create_package,
)


class TestBuildDesignPrinciplesMessages:
    def test_builds_messages(
        self,
        mocker: MockerFixture,
    ) -> None:
        context = create_llm_context_build_context(
            knowledge=create_llm_knowledge(
                package=create_package(
                    policies=("Policy 1", "Policy 2"),
                    constraints=("Constraint 1", "Constraint 2"),
                    rationale=("Rationale 1", "Rationale 2"),
                ),
            ),
        )

        load_prompt = mocker.patch(
            "gyomu_ai_compiler.pipelines.llm_context.renderer.design_principles.load_prompt",
            return_value=Success("design principles prompt"),
        )

        result = build_design_principles_messages(context)

        assert isinstance(result, Success)

        conversation = result.unwrap()

        assert conversation.system
        assert conversation.system.parts[0].text == "design principles prompt"

        assert conversation.request
        assert len(conversation.request.parts) == 1
        assert conversation.request.parts[0] is not None

        msg = conversation.request.parts[0].text

        user_data = json.loads(msg)

        assert user_data == {
            "policies": ["Policy 1", "Policy 2"],
            "constraints": ["Constraint 1", "Constraint 2"],
            "rationale": ["Rationale 1", "Rationale 2"],
        }

        load_prompt.assert_called_once_with(name="llm_context/design-principles.md")

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
            "gyomu_ai_compiler.pipelines.llm_context.renderer.design_principles.load_prompt",
            return_value=Failure(error),
        )

        result = build_design_principles_messages(create_llm_context_build_context())

        assert result == Failure(error)
