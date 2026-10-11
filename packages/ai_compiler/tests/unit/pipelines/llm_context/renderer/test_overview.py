from gyomu_ai_compiler.pipelines.llm_context.renderer.overview import (
    build_overview_messages,
)
from gyomu_schema.error.io import GyomuIOError, IOLayer, IOOperation
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.schema.schema_test_support.concept_helpers import (
    create_llm_context_build_context,
    create_llm_knowledge,
    create_package,
    create_package_concept,
)


class TestBuildOverviewMessages:
    def test_builds_messages(
        self,
        mocker: MockerFixture,
    ) -> None:
        context = create_llm_context_build_context(
            concept=create_package_concept(
                summary="Package concept summary",
            ),
            knowledge=create_llm_knowledge(
                package=create_package(
                    mission="Package mission",
                ),
            ),
        )

        load_prompt = mocker.patch(
            "gyomu_ai_compiler.pipelines.llm_context.renderer.overview.load_prompt",
            return_value=Success("overview prompt"),
        )

        result = build_overview_messages(context)

        assert isinstance(result, Success)

        conversation = result.unwrap()

        assert conversation.system
        assert conversation.system.parts[0].text == "overview prompt"

        assert conversation.request
        assert len(conversation.request.parts) == 1
        assert conversation.request.parts[0] is not None

        msg = conversation.request.parts[0].text

        assert '"mission": "Package mission"' in msg
        assert '"concept_summary": "Package concept summary"' in msg

        load_prompt.assert_called_once_with(name="llm_context/overview-generate.md")

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
            "gyomu_ai_compiler.pipelines.llm_context.renderer.overview.load_prompt",
            return_value=Failure(error),
        )

        result = build_overview_messages(create_llm_context_build_context())

        assert result == Failure(error)
