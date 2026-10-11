from pathlib import Path

from gyomu_ai_compiler.pipelines.llm_context.renderer.architecture import (
    build_architecture_messages,
)
from gyomu_facts.package.analysis import TopScoreDirectorySelection
from gyomu_schema.error.io import GyomuIOError, IOLayer, IOOperation
from gyomu_schema.schemas.python.types import ProjectRelativePath
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.schema.schema_test_support.concept_helpers import (
    create_llm_context_build_context,
)


class TestBuildArchitectureMessages:
    def test_builds_messages(
        self,
        mocker: MockerFixture,
    ) -> None:
        context = create_llm_context_build_context()

        load_prompt = mocker.patch(
            "gyomu_ai_compiler.pipelines.llm_context.renderer.architecture.load_prompt",
            return_value=Success("architecture prompt"),
        )

        result = build_architecture_messages(context)

        assert isinstance(result, Success)

        conversation = result.unwrap()

        assert conversation.system
        assert conversation.system.parts[0].text == "architecture prompt"
        assert conversation.request
        assert len(conversation.request.parts) == 1

        load_prompt.assert_called_once_with(name="llm_context/architecture-generate.md")

    def test_top_directories(
        self,
        mocker: MockerFixture,
    ) -> None:
        context = create_llm_context_build_context()

        ranked = [
            mocker.Mock(
                path=ProjectRelativePath(Path("src/core")),
                concept=mocker.Mock(
                    summary="Core directory",
                    responsibilities=["Core responsibility"],
                    relationships=["Core relationship"],
                ),
            ),
        ]

        get_ranked = mocker.patch(
            "gyomu_ai_compiler.pipelines.llm_context.renderer.architecture"
            ".PackageFacts.get_ranked_directories",
            return_value=ranked,
        )

        result = build_architecture_messages(context)

        assert isinstance(result, Success)

        user_message = result.unwrap().request
        assert user_message
        assert user_message.parts[0] is not None
        msg = user_message.parts[0].text

        assert '"path": "src/core"' in msg
        assert '"summary": "Core directory"' in msg
        assert '"Core responsibility"' in msg
        assert '"Core relationship"' in msg

        get_ranked.assert_called_once_with(TopScoreDirectorySelection(limit=5))

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
            "gyomu_ai_compiler.pipelines.llm_context.renderer.architecture.load_prompt",
            return_value=Failure(error),
        )

        result = build_architecture_messages(create_llm_context_build_context())

        assert result == Failure(error)
