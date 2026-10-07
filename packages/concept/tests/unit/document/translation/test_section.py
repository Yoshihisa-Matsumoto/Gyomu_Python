import pytest
from gyomu_concept.document.translation.section import translate_section
from gyomu_schema.error.translation import TranslationError
from gyomu_schema.schemas.document.section import BuiltSection
from gyomu_schema.schemas.document.translation.code import (
    code_block_translation_strategy,
)
from gyomu_schema.schemas.document.translation.paragraph import (
    paragraph_translation_strategy,
)
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.schema.schema_test_support.concept_helpers import (
    create_codeblock,
    create_paragraph,
    create_section,
    create_section_no_translation,
    create_section_translation_instruction,
)


class TestTranslateSection:
    @pytest.mark.asyncio
    async def test_returns_original_contents_without_translation(
        self,
    ) -> None:
        paragraph = create_paragraph(text="Original")
        section = create_section(
            id="overview",
            title="Overview",
            contents=(paragraph,),
        )
        built_section = BuiltSection(
            section=section,
            translation=create_section_no_translation(),
        )

        result = await translate_section(
            section=built_section,
            language="ja",
        )

        assert isinstance(result, Success)

        translated = result.unwrap()

        assert translated.id == section.id
        assert translated.title == section.title
        assert translated.contents == (paragraph,)

    @pytest.mark.asyncio
    async def test_translates_all_contents(
        self,
        mocker: MockerFixture,
    ) -> None:
        paragraph = create_paragraph(text="Original paragraph")
        code = create_codeblock(
            language="python",
            code="print('hello')",
        )

        section = create_section(
            id="overview",
            title="Overview",
            contents=(paragraph, code),
        )

        strategy1 = paragraph_translation_strategy
        strategy2 = code_block_translation_strategy

        translation = create_section_translation_instruction(
            translation_instruction="Translate the content.",
            translation_strategies=(strategy1, strategy2),
        )

        built_section = BuiltSection(
            section=section,
            translation=translation,
        )

        translated_paragraph = create_paragraph(text="翻訳された段落")
        translated_code = create_codeblock(
            language="python",
            code="print('こんにちは')",
        )

        execute_mock = mocker.patch(
            "gyomu_concept.document.translation.section"
            ".execute_document_content_translation",
            side_effect=[
                Success(translated_paragraph),
                Success(translated_code),
            ],
        )

        result = await translate_section(
            section=built_section,
            language="ja",
        )

        assert isinstance(result, Success)

        translated = result.unwrap()

        assert translated.id == section.id
        assert translated.title == section.title
        assert translated.contents == (
            translated_paragraph,
            translated_code,
        )

        assert execute_mock.call_count == 2

    @pytest.mark.asyncio
    async def test_returns_translation_failure(
        self,
        mocker: MockerFixture,
    ) -> None:
        paragraph = create_paragraph(text="Original")

        section = create_section(
            id="overview",
            contents=(paragraph,),
        )

        translation = create_section_translation_instruction(
            translation_strategies=(paragraph_translation_strategy,),
        )

        built_section = BuiltSection(
            section=section,
            translation=translation,
        )

        error = TranslationError(
            "Failed to translate content.",
            phase="translate",
            section_id="1",
            content_type="paragraph",
        )

        mocker.patch(
            "gyomu_concept.document.translation.section"
            ".execute_document_content_translation",
            return_value=Failure(error),
        )

        result = await translate_section(
            section=built_section,
            language="ja",
        )

        assert isinstance(result, Failure)
        assert result.failure() is error

    @pytest.mark.asyncio
    async def test_stops_translation_after_failure(
        self,
        mocker: MockerFixture,
    ) -> None:
        paragraph1 = create_paragraph(text="First")
        paragraph2 = create_paragraph(text="Second")
        paragraph3 = create_paragraph(text="Third")

        section = create_section(
            id="overview",
            contents=(paragraph1, paragraph2, paragraph3),
        )

        strategy1 = paragraph_translation_strategy
        strategy2 = paragraph_translation_strategy
        strategy3 = paragraph_translation_strategy

        translation = create_section_translation_instruction(
            translation_strategies=(strategy1, strategy2, strategy3),
        )

        built_section = BuiltSection(
            section=section,
            translation=translation,
        )

        error = TranslationError(
            "Failed to translate content.",
            phase="translate",
            section_id="1",
            content_type="paragraph",
        )

        translated_paragraph1 = create_paragraph(text="First translated")

        execute_mock = mocker.patch(
            "gyomu_concept.document.translation.section"
            ".execute_document_content_translation",
            side_effect=[
                Success(translated_paragraph1),
                Failure(error),
            ],
        )

        result = await translate_section(
            section=built_section,
            language="ja",
        )

        assert isinstance(result, Failure)
        assert result.failure() is error

        assert execute_mock.call_count == 2

        first_call = execute_mock.call_args_list[0]
        second_call = execute_mock.call_args_list[1]

        assert first_call.kwargs == {
            "language": "ja",
            "section_id": "overview",
            "context": paragraph1,
            "section_definition": translation,
            "content_strategy": strategy1,
        }

        assert second_call.kwargs == {
            "language": "ja",
            "section_id": "overview",
            "context": paragraph2,
            "section_definition": translation,
            "content_strategy": strategy2,
        }
