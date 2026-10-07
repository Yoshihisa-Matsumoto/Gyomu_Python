import pytest
from gyomu_concept.document.builder.section import SectionBuilder, build_sections
from gyomu_concept.error.document import DocumentBuilderError
from gyomu_schema.schemas.concept.base import DocumentBaseContext
from gyomu_schema.schemas.document.section import (
    SectionNoTranslation,
    SectionTranslationInstruction,
)
from gyomu_schema.schemas.document.translation.bullet_list import (
    bullet_list_translation_strategy,
)
from gyomu_schema.schemas.document.translation.code import (
    code_block_translation_strategy,
)
from gyomu_schema.schemas.document.translation.paragraph import (
    paragraph_translation_strategy,
)
from gyomu_schema.schemas.document.translation.table import (
    table_translation_strategy,
)
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.schema.schema_test_support.concept_helpers import (
    create_bullet_list,
    create_bullet_list_item,
    create_codeblock,
    create_document_base_context,
    create_paragraph,
    create_section,
    create_section_no_translation,
    create_section_translation_instruction,
    create_section_with_instruction,
    create_table,
    create_table_row,
)


class TestBuildSections:
    @pytest.fixture
    def context(self) -> DocumentBaseContext:
        return create_document_base_context()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("enabled", "expected_count"),
        [
            (True, 1),
            (False, 0),
        ],
    )
    async def test_builds_only_enabled_sections(
        self,
        mocker: MockerFixture,
        context: DocumentBaseContext,
        enabled: bool,
        expected_count: int,
    ) -> None:
        section = create_section()
        section_with_instruction = create_section_with_instruction(section=section)
        enabled_mock = mocker.Mock(return_value=enabled)
        build_mock = mocker.AsyncMock(return_value=Success(section_with_instruction))

        builder = SectionBuilder(
            id="test-section",
            translation=create_section_translation_instruction(),
            build=build_mock,
            enabled=enabled_mock,
        )

        result = await build_sections(
            context=context,
            builders=(builder,),
        )

        assert isinstance(result, Success)
        assert len(result.unwrap()) == expected_count

        enabled_mock.assert_called_once_with(context)

        if enabled:
            build_mock.assert_awaited_once_with(context, None)
        else:
            build_mock.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_returns_build_failure(
        self,
        mocker: MockerFixture,
        context: DocumentBaseContext,
    ) -> None:
        error = DocumentBuilderError("Failed to build section.", phase="context-build")

        builder = SectionBuilder(
            id="test-section",
            translation=create_section_translation_instruction(),
            build=mocker.AsyncMock(return_value=Failure(error)),
            enabled=mocker.Mock(return_value=True),
        )

        result = await build_sections(
            context=context,
            builders=(builder,),
        )

        assert isinstance(result, Failure)
        assert result.failure() is error

    @pytest.mark.asyncio
    async def test_builds_section_without_translation(
        self,
        mocker: MockerFixture,
        context: DocumentBaseContext,
    ) -> None:
        section = create_section()
        section_with_instruction = create_section_with_instruction(section=section)

        builder = SectionBuilder(
            id="test-section",
            translation=create_section_no_translation(),
            build=mocker.AsyncMock(return_value=Success(section_with_instruction)),
            enabled=mocker.Mock(return_value=True),
        )

        result = await build_sections(
            context=context,
            builders=(builder,),
        )

        assert isinstance(result, Success)

        built_section = result.unwrap()[0]

        assert built_section.section is section_with_instruction.section
        assert isinstance(built_section.translation, SectionNoTranslation)

    @pytest.mark.asyncio
    async def test_builds_section_with_translation(
        self,
        mocker: MockerFixture,
        context: DocumentBaseContext,
    ) -> None:
        section = create_section()
        section_with_instruction = create_section_with_instruction(section=section)

        section_with_instruction.translation_instruction = "Translate this section."

        builder = SectionBuilder(
            id="test-section",
            translation=create_section_translation_instruction(),
            build=mocker.AsyncMock(return_value=Success(section_with_instruction)),
            enabled=mocker.Mock(return_value=True),
        )

        result = await build_sections(
            context=context,
            builders=(builder,),
        )

        assert isinstance(result, Success)

        built_section = result.unwrap()[0]

        assert built_section.section is section_with_instruction.section
        assert isinstance(
            built_section.translation,
            SectionTranslationInstruction,
        )

        translation = built_section.translation

        assert (
            translation.translation_instruction
            == section_with_instruction.translation_instruction
        )

    @pytest.mark.asyncio
    async def test_selects_translation_strategy_for_each_content_kind(
        self,
        mocker: MockerFixture,
        context: DocumentBaseContext,
    ) -> None:
        section = create_section()
        section_with_instruction = create_section_with_instruction(section=section)

        section_with_instruction.translation_instruction = "Translate this section."

        paragraph = create_paragraph()
        bullet_list = create_bullet_list(
            items=(create_bullet_list_item(translation_id=1, text="one"),)
        )
        code_block = create_codeblock()
        table = create_table(
            header=create_table_row(
                cells=("Name", "Description"),
            ),
            rows=(
                create_table_row(
                    cells=("Alice", "Engineer"),
                ),
            ),
        )

        section_with_instruction.section.contents = (
            paragraph,
            bullet_list,
            code_block,
            table,
        )

        builder = SectionBuilder(
            id="test-section",
            translation=create_section_translation_instruction(),
            build=mocker.AsyncMock(return_value=Success(section_with_instruction)),
            enabled=mocker.Mock(return_value=True),
        )

        result = await build_sections(
            context=context,
            builders=(builder,),
        )

        assert isinstance(result, Success)

        translation = result.unwrap()[0].translation

        assert isinstance(translation, SectionTranslationInstruction)
        assert translation.translation_strategies == (
            paragraph_translation_strategy,
            bullet_list_translation_strategy,
            code_block_translation_strategy,
            table_translation_strategy,
        )

    @pytest.mark.asyncio
    async def test_builds_multiple_sections_in_order(
        self,
        mocker: MockerFixture,
        context: DocumentBaseContext,
    ) -> None:
        section1 = create_section_with_instruction(
            section=create_section(),
        )
        section2 = create_section_with_instruction(
            section=create_section(id="dummy"),
        )

        builder1 = SectionBuilder(
            id="section-1",
            translation=create_section_translation_instruction(),
            build=mocker.AsyncMock(return_value=Success(section1)),
            enabled=mocker.Mock(return_value=True),
        )
        builder2 = SectionBuilder(
            id="section-2",
            translation=create_section_translation_instruction(),
            build=mocker.AsyncMock(return_value=Success(section2)),
            enabled=mocker.Mock(return_value=True),
        )

        result = await build_sections(
            context=context,
            builders=(builder1, builder2),
        )

        assert isinstance(result, Success)
        sections = result.unwrap()

        assert len(sections) == 2
        assert sections[0].section is section1.section
        assert sections[1].section is section2.section
