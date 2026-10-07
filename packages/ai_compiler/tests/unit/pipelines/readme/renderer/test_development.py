from gyomu_ai_compiler.pipelines.readme.renderer.development import (
    build_development_messages,
)
from gyomu_schema.error.io import GyomuIOError, IOLayer, IOOperation
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.schema.schema_test_support.concept_helpers import (
    create_document_base_context,
    create_knowledge,
    create_package,
    create_package_concept,
)


class TestBuildDevelopmentMessages:
    def test_builds_messages(
        self,
        mocker: MockerFixture,
    ) -> None:
        context = create_document_base_context(
            concept=create_package_concept(
                responsibilities=["responsibility1", "responsibility2"]
            )
        )

        load_prompt = mocker.patch(
            "gyomu_ai_compiler.pipelines.readme.renderer.development.load_prompt",
            return_value=Success(
                "Mission: {{MISSION}}\n"
                "Responsibilities:\n{{RESPONSIBILITIES}}\n"
                "Policies:\n{{POLICY}}"
            ),
        )

        result = build_development_messages(context)

        assert isinstance(result, Success)

        conversation = result.unwrap()

        assert conversation.request is not None
        assert len(conversation.request.parts) == 1
        assert conversation.request.parts[0] is not None

        text = conversation.request.parts[0].text

        assert "Mission: Mission 1" in text
        assert "- responsibility1" in text
        assert "- responsibility2" in text
        assert "Policy 1" in text

        assert "{{MISSION}}" not in text
        assert "{{RESPONSIBILITIES}}" not in text
        assert "{{POLICY}}" not in text

        load_prompt.assert_called_once_with(name="readme/development-assemble.md")

    def test_replaces_responsibilities_and_policies(
        self,
    ) -> None:
        context = create_document_base_context(
            concept=create_package_concept(
                responsibilities=[
                    "First responsibility",
                    "Second responsibility",
                ],
            ),
            knowledge=create_knowledge(
                package=create_package(
                    mission="Package mission",
                    policies=(
                        "First policy",
                        "Second policy",
                    ),
                ),
            ),
        )

        result = build_development_messages(context)

        assert isinstance(result, Success)

        request = result.unwrap().request
        assert request is not None
        assert request.parts[0] is not None

        text = request.parts[0].text

        assert "- First responsibility\n- Second responsibility" in text
        assert "First policy\nSecond policy" in text

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
            "gyomu_ai_compiler.pipelines.readme.renderer.development.load_prompt",
            return_value=Failure(error),
        )

        result = build_development_messages(create_document_base_context())

        assert result == Failure(error)
