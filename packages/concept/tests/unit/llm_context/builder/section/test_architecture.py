from gyomu_ai_compiler.pipelines.llm_context.prompt import llm_context_prompt_provider
from gyomu_concept.error.document import DocumentBuilderError
from gyomu_concept.llm_context.builder.section.architecture import (
    _build,
    _enabled,
    build_architecture,
)
from gyomu_schema.error.ai import (
    AiError,
    AiErrorPhase,
    AiFailResolution,
    AiOperation,
)
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.llm_context.types import LlmContextSectionId
from gyomu_schema.schemas.document.content import Paragraph
from gyomu_schema.schemas.document.section import (
    Section,
    SectionNoTranslation,
    SectionWithInstruction,
)
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.schema.schema_test_support.concept_helpers import (
    create_llm_context_build_context,
)


class TestBuildArchitecture:
    async def test_builds_section(
        self,
        mocker: MockerFixture,
    ) -> None:
        context = create_llm_context_build_context()
        option = ConceptOption()

        build_section_item_mock = mocker.patch(
            "gyomu_concept.llm_context.builder.section.architecture.build_section_item",
            new_callable=mocker.AsyncMock,
            return_value=Success("Architecture description"),
        )

        result = await _build(context, option)

        assert result == Success(
            SectionWithInstruction[LlmContextSectionId](
                section=Section[LlmContextSectionId](
                    id="architecture",
                    contents=(Paragraph(text="Architecture description"),),
                ),
            )
        )

        build_section_item_mock.assert_awaited_once_with(
            "architecture",
            context,
            llm_context_prompt_provider,
        )

    async def test_propagates_build_failure(
        self,
        mocker: MockerFixture,
    ) -> None:
        context = create_llm_context_build_context()
        error = AiError(
            "failed to build architecture",
            operation=AiOperation.GENERATE,
            model_key=None,
            model=None,
            phase=AiErrorPhase.REQUEST,
            resolution=AiFailResolution(),
        )

        build_section_item_mock = mocker.patch(
            "gyomu_concept.llm_context.builder.section.architecture.build_section_item",
            new_callable=mocker.AsyncMock,
            return_value=Failure(error),
        )

        result = await _build(context)

        assert isinstance(result, Failure)

        document_error = result.failure()

        assert isinstance(document_error, DocumentBuilderError)
        assert document_error.package_name == context.analysis.package.name
        assert document_error.phase == "section-build"
        assert document_error.section_id == "architecture"
        assert document_error.__cause__ is not None

        build_section_item_mock.assert_awaited_once_with(
            "architecture",
            context,
            llm_context_prompt_provider,
        )

    def test_enabled(
        self,
    ) -> None:
        context = create_llm_context_build_context()

        assert _enabled(context) is True


class TestBuildArchitectureDefinition:
    def test_definition(
        self,
    ) -> None:
        assert build_architecture.id == "architecture"
        assert build_architecture.enabled is _enabled
        assert build_architecture.build is _build
        assert build_architecture.translation == SectionNoTranslation()
