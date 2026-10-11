from gyomu_ai_compiler.pipelines.llm_context.prompt import (
    llm_context_prompt_provider,
)
from gyomu_concept.error.document import DocumentBuilderError
from gyomu_concept.llm_context.builder.section.design_principles import (
    _build,
    _enabled,
    build_design_principles,
)
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.llm_context.types import LlmContextSectionId
from gyomu_schema.schemas.document.content import BulletList, BulletListItem
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


class TestBuildDesignPrinciples:
    async def test_builds_section(self, mocker: MockerFixture) -> None:
        context = create_llm_context_build_context()
        option = ConceptOption()
        bullet_list = BulletList(
            items=(
                BulletListItem(
                    translation_id=0,
                    text="Keep dependencies explicit",
                ),
                BulletListItem(
                    translation_id=1,
                    text="Prefer simple abstractions",
                ),
            )
        )
        build_bullet_list_mock = mocker.patch(
            "gyomu_concept.llm_context.builder.section.design_principles.build_bullet_list",
            new_callable=mocker.AsyncMock,
            return_value=Success(bullet_list),
        )

        result = await _build(context, option)

        assert result == Success(
            SectionWithInstruction[LlmContextSectionId](
                section=Section[LlmContextSectionId](
                    id="design-principles",
                    contents=(bullet_list,),
                ),
            )
        )
        build_bullet_list_mock.assert_awaited_once_with(
            "design-principles",
            context,
            llm_context_prompt_provider,
        )

    async def test_propagates_build_failure(self, mocker: MockerFixture) -> None:
        context = create_llm_context_build_context()
        error = DocumentBuilderError(
            "failed to build bullet list",
            package_name=context.analysis.package.name,
            phase="section-build",
            section_id="design-principles",
        )
        build_bullet_list_mock = mocker.patch(
            "gyomu_concept.llm_context.builder.section.design_principles.build_bullet_list",
            new_callable=mocker.AsyncMock,
            return_value=Failure(error),
        )

        result = await _build(context)

        assert isinstance(result, Failure)
        document_error = result.failure()
        assert isinstance(document_error, DocumentBuilderError)
        assert document_error.package_name == context.analysis.package.name
        assert document_error.phase == "section-build"
        assert document_error.section_id == "design-principles"
        assert document_error.__cause__ is not None
        build_bullet_list_mock.assert_awaited_once_with(
            "design-principles",
            context,
            llm_context_prompt_provider,
        )

    def test_enabled(self) -> None:
        context = create_llm_context_build_context()

        assert _enabled(context) is True


class TestBuildDesignPrinciplesDefinition:
    def test_definition(self) -> None:
        assert build_design_principles.id == "design-principles"
        assert build_design_principles.enabled is _enabled
        assert build_design_principles.build is _build
        assert build_design_principles.translation == SectionNoTranslation()
