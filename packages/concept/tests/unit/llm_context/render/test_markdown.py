from gyomu_concept.document.translation.document import TranslatedDocument
from gyomu_concept.llm_context.render.markdown import render_llm_context_markdown
from gyomu_schema.schemas.concept.llm_context.types import LlmContextSectionId
from gyomu_schema.schemas.document.content import Paragraph
from gyomu_schema.schemas.document.section import LanguageCodes, Section

from packages.schema.schema_test_support.concept_helpers import (
    create_llm_context_build_context,
    create_package_analysis__default,
)


def create_translated_document(
    language: LanguageCodes = "en",
    sections: tuple[Section[LlmContextSectionId], ...] = (),
) -> TranslatedDocument[LlmContextSectionId]:
    return TranslatedDocument[LlmContextSectionId](
        language=language,
        sections=sections,
    )


class TestRenderReadmeMarkdown:
    def test_renders_title_and_section(self) -> None:
        context = create_llm_context_build_context(
            analysis=create_package_analysis__default()
        )
        context.analysis.package.name = "gyomu-test"
        context.knowledge.package.display_name = "gyomu-test"
        plan = create_translated_document(
            language="en",
            sections=(
                Section[LlmContextSectionId](
                    id="overview",
                    contents=(Paragraph(text="Overview text."),),
                ),
            ),
        )

        result = render_llm_context_markdown(context, plan)

        assert (
            result
            == """# gyomu-test

## Repository Overview

Overview text."""
        )

    def test_uses_explicit_section_title(self) -> None:
        context = create_llm_context_build_context()
        context.knowledge.package.display_name = "Package"
        plan = create_translated_document(
            language="en",
            sections=(
                Section(
                    id="overview",
                    title="Custom Overview",
                    contents=(Paragraph(text="Overview text."),),
                ),
            ),
        )

        result = render_llm_context_markdown(context, plan)

        assert (
            result
            == """# Package

## Custom Overview

Overview text."""
        )

    def test_does_not_render_language_link_when_not_needed(self) -> None:
        context = create_llm_context_build_context()
        plan = create_translated_document(
            language="en",
            sections=(
                Section(
                    id="overview",
                    contents=(Paragraph(text="Overview text."),),
                ),
            ),
        )

        result = render_llm_context_markdown(
            context,
            plan,
            need_link=False,
        )

        assert "US English" not in result
        assert "README.ja.md" not in result
