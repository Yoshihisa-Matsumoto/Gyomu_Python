from gyomu_concept.document.render.markdown import render_markdown
from gyomu_concept.document.translation.document import TranslatedDocument
from gyomu_schema.schemas.concept.base import DocumentBaseContext
from gyomu_schema.schemas.document.section import LanguageCodes, Section

from packages.schema.schema_test_support.concept_helpers import (
    create_bullet_list,
    create_bullet_list_item,
    create_codeblock,
    create_document_base_context,
    create_paragraph,
    create_section,
    create_table,
    create_table_row,
)


class TestRenderMarkdown:
    def test_render(self) -> None:
        sections: tuple[Section, ...] = (
            create_section(
                id="overview",
                title="Overview",
                contents=(
                    create_paragraph(text="This package provides shared utilities."),
                    create_bullet_list(
                        items=(
                            create_bullet_list_item(translation_id=1, text="Item1"),
                            create_bullet_list_item(translation_id=2, text="Item2"),
                        )
                    ),
                    create_codeblock(
                        language="ts", title="Example", code='console.log("hello")'
                    ),
                    create_table(
                        header=create_table_row(
                            cells=(
                                "Header1",
                                "Header2",
                            )
                        ),
                        rows=(
                            create_table_row(cells=("R1C1", "R1C2")),
                            create_table_row(cells=("R2C1", "R2C2")),
                        ),
                    ),
                ),
            ),
        )

        def _get_title(context: DocumentBaseContext) -> str:
            return "TITLE"

        def _get_section_title(code: LanguageCodes, section: Section) -> str:
            return "Overview"

        markdown = render_markdown(
            context=create_document_base_context(),
            plan=TranslatedDocument(language="en", sections=sections),
            get_title=_get_title,
            get_section_title=_get_section_title,
        )
        assert (
            markdown
            == """# TITLE

## Overview

This package provides shared utilities.

- Item1
- Item2

### Example

```ts
console.log("hello")
```

| Header1 | Header2 |
| ------- | ------- |
| R1C1 | R1C2 |
| R2C1 | R2C2 |"""
        )

    def test_render_multiple_sections(self) -> None:
        sections: tuple[Section, ...] = (
            create_section(
                id="overview",
                title="Overview",
                contents=(create_paragraph(text="First section."),),
            ),
            create_section(
                id="development",
                title="Development",
                contents=(create_paragraph(text="Second section."),),
            ),
        )

        def _get_title(context: DocumentBaseContext) -> str:
            return "TITLE"

        def _get_section_title(language: LanguageCodes, section: Section) -> str:
            return section.title or ""

        markdown = render_markdown(
            context=create_document_base_context(),
            plan=TranslatedDocument(language="en", sections=sections),
            get_title=_get_title,
            get_section_title=_get_section_title,
        )

        assert (
            markdown
            == """# TITLE

## Overview

First section.

## Development

Second section."""
        )

    def test_render_empty_section(self) -> None:
        sections: tuple[Section, ...] = (
            create_section(
                id="overview",
                title="Overview",
                contents=(),
            ),
        )

        def _get_title(context: DocumentBaseContext) -> str:
            return "TITLE"

        def _get_section_title(language: LanguageCodes, section: Section) -> str:
            return "Overview"

        markdown = render_markdown(
            context=create_document_base_context(),
            plan=TranslatedDocument(language="en", sections=sections),
            get_title=_get_title,
            get_section_title=_get_section_title,
        )

        assert (
            markdown
            == """# TITLE

## Overview

"""
        )

    def test_render_with_language_link(self) -> None:
        sections: tuple[Section, ...] = (
            create_section(
                id="overview",
                title="Overview",
                contents=(),
            ),
        )

        def _get_title(context: DocumentBaseContext) -> str:
            return "TITLE"

        def _get_section_title(language: LanguageCodes, section: Section) -> str:
            return "Overview"

        def _get_language_link(
            language: LanguageCodes,
            plan: TranslatedDocument,
        ) -> str:
            if language == "en":
                return "US English"
            return "[JP 日本語](README.ja.md)"

        markdown = render_markdown(
            context=create_document_base_context(),
            plan=TranslatedDocument(language="en", sections=sections),
            get_title=_get_title,
            get_section_title=_get_section_title,
            get_language_link=_get_language_link,
        )

        assert (
            markdown
            == """# TITLE

US English | [JP 日本語](README.ja.md)

## Overview

"""
        )

    def test_render_nested_bullet_lists(self) -> None:
        sections: tuple[Section, ...] = (
            create_section(
                id="overview",
                title="Overview",
                contents=(
                    create_bullet_list(
                        items=(
                            create_bullet_list_item(
                                translation_id=1,
                                text="Item1",
                            ),
                            create_bullet_list_item(
                                translation_id=2,
                                text="Item2",
                                children=(
                                    create_bullet_list_item(
                                        translation_id=3,
                                        text="SubItem1",
                                        children=(
                                            create_bullet_list_item(
                                                translation_id=5,
                                                text="SubSubItem1",
                                            ),
                                        ),
                                    ),
                                    create_bullet_list_item(
                                        translation_id=4,
                                        text="SubItem2",
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        )

        def _get_title(context: DocumentBaseContext) -> str:
            return "TITLE"

        def _get_section_title(language: LanguageCodes, section: Section) -> str:
            return "Overview"

        markdown = render_markdown(
            context=create_document_base_context(),
            plan=TranslatedDocument(language="en", sections=sections),
            get_title=_get_title,
            get_section_title=_get_section_title,
        )

        assert (
            markdown
            == """# TITLE

## Overview

- Item1
- Item2
  - SubItem1
    - SubSubItem1
  - SubItem2"""
        )
