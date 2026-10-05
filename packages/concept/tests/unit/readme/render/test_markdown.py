from gyomu_concept.document.translation.document import TranslatedDocument
from gyomu_concept.readme.render.markdown import render_readme_markdown
from gyomu_schema.schemas.concept.readme.types import ReadmeSectionId
from gyomu_schema.schemas.document.content import Paragraph
from gyomu_schema.schemas.document.section import LanguageCodes, Section

from packages.schema.schema_test_support.concept_helpers import (
    create_document_base_context,
    create_package_analysis__default,
)


def create_translated_document(
    language: LanguageCodes = "en",
    sections: tuple[Section[ReadmeSectionId], ...] = (),
) -> TranslatedDocument[ReadmeSectionId]:
    return TranslatedDocument[ReadmeSectionId](
        language=language,
        sections=sections,
    )


class TestRenderReadmeMarkdown:
    def test_renders_title_and_section(self) -> None:
        context = create_document_base_context(
            analysis=create_package_analysis__default()
        )
        context.analysis.package.name = "gyomu-test"
        context.knowledge.package.display_name = "gyomu-test"
        plan = create_translated_document(
            language="en",
            sections=(
                Section[ReadmeSectionId](
                    id="overview",
                    contents=(Paragraph(text="Overview text."),),
                ),
            ),
        )

        result = render_readme_markdown(context, plan)

        assert (
            result
            == """# gyomu-test

## Overview

Overview text."""
        )

    def test_uses_explicit_section_title(self) -> None:
        context = create_document_base_context()
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

        result = render_readme_markdown(context, plan)

        assert (
            result
            == """# Package

## Custom Overview

Overview text."""
        )

    def test_does_not_render_language_link_when_not_needed(self) -> None:
        context = create_document_base_context()
        plan = create_translated_document(
            language="en",
            sections=(
                Section(
                    id="overview",
                    contents=(Paragraph(text="Overview text."),),
                ),
            ),
        )

        result = render_readme_markdown(
            context,
            plan,
            need_link=False,
        )

        assert "US English" not in result
        assert "README.ja.md" not in result

    def test_renders_current_language_without_link(self) -> None:
        context = create_document_base_context()
        plan = create_translated_document(
            language="en",
            sections=(
                Section(
                    id="overview",
                    contents=(Paragraph(text="Overview text."),),
                ),
            ),
        )

        result = render_readme_markdown(
            context,
            plan,
            need_link=True,
        )

        assert "US English" in result
        assert "[US English]" not in result
        assert "README.ja.md" in result

    def test_renders_other_language_as_link(self) -> None:
        context = create_document_base_context()
        plan = create_translated_document(
            language="ja",
            sections=(
                Section(
                    id="overview",
                    contents=(Paragraph(text="概要です。"),),
                ),
            ),
        )

        result = render_readme_markdown(
            context,
            plan,
            need_link=True,
        )

        assert "JP 日本語" in result
        assert "[JP 日本語](README.ja.md)" not in result
        assert "[US English](README.md)" in result
