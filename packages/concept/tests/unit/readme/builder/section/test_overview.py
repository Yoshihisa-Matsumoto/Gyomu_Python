from gyomu_ai_compiler.pipelines.readme.prompt import readme_prompt_provider
from gyomu_concept.error.document import DocumentBuilderError
from gyomu_concept.readme.builder.section.overview import (
    _build,
    _enabled,
    build_overview,
)
from gyomu_schema.error.ai import (
    AiError,
    AiErrorPhase,
    AiFailResolution,
    AiOperation,
)
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.readme.types import ReadmeSectionId
from gyomu_schema.schemas.document.content import Paragraph
from gyomu_schema.schemas.document.section import (
    Section,
    SectionTranslationInstruction,
    SectionWithInstruction,
)
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.schema.schema_test_support.concept_helpers import (
    create_document_base_context,
)


class TestBuildOverview:
    async def test_builds_section(
        self,
        mocker: MockerFixture,
    ) -> None:
        context = create_document_base_context()
        option = ConceptOption()

        build_section_item_mock = mocker.patch(
            "gyomu_concept.readme.builder.section.overview.build_section_item",
            new_callable=mocker.AsyncMock,
            return_value=Success("Overview description"),
        )

        result = await _build(context, option)

        assert result == Success(
            SectionWithInstruction[ReadmeSectionId](
                section=Section[ReadmeSectionId](
                    id="overview",
                    contents=(Paragraph(text="Overview description"),),
                ),
            )
        )

        build_section_item_mock.assert_awaited_once_with(
            "overview",
            context,
            readme_prompt_provider,
        )

    async def test_propagates_build_failure(
        self,
        mocker: MockerFixture,
    ) -> None:
        context = create_document_base_context()
        error = AiError(
            "failed to build overview",
            operation=AiOperation.GENERATE,
            model_key=None,
            model=None,
            phase=AiErrorPhase.REQUEST,
            resolution=AiFailResolution(),
        )

        build_section_item_mock = mocker.patch(
            "gyomu_concept.readme.builder.section.overview.build_section_item",
            new_callable=mocker.AsyncMock,
            return_value=Failure(error),
        )

        result = await _build(context)

        assert isinstance(result, Failure)

        document_error = result.failure()

        assert isinstance(document_error, DocumentBuilderError)
        assert document_error.package_name == context.analysis.package.name
        assert document_error.phase == "section-build"
        assert document_error.section_id == "overview"
        assert document_error.__cause__ is not None

        build_section_item_mock.assert_awaited_once_with(
            "overview",
            context,
            readme_prompt_provider,
        )

    def test_enabled(
        self,
    ) -> None:
        context = create_document_base_context()

        assert _enabled(context) is True


class TestBuildOverviewDefinition:
    def test_definition(
        self,
    ) -> None:
        assert build_overview.id == "overview"
        assert build_overview.enabled is _enabled
        assert build_overview.build is _build
        assert build_overview.translation == (
            SectionTranslationInstruction(translation_strategies=())
        )
