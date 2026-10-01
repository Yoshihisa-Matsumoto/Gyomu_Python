from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from gyomu_concept.error.document import DocumentBuilderError
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.base import DocumentBaseContext
from gyomu_schema.schemas.document.content import DocumentContent, DocumentContentType
from gyomu_schema.schemas.document.section import (
    BuiltSection,
    DocumentContentTranslationStrategy,
    SectionNoTranslation,
    SectionTranslationDefinition,
    SectionTranslationInstruction,
    SectionWithInstruction,
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
from gyomu_schema.schemas.document.translation.table import table_translation_strategy
from returns.result import Failure, Result, Success


@dataclass
class SectionBuilder[
    TSectionId: str,
    TContext: DocumentBaseContext,
]:
    id: TSectionId
    translation: SectionTranslationDefinition
    build: Callable[
        [TContext, ConceptOption | None],
        Result[SectionWithInstruction, DocumentBuilderError],
    ]
    enabled: Callable[[TContext], bool]


def _get_translation_strategy(
    content: DocumentContent,
) -> DocumentContentTranslationStrategy[Any]:
    match content.kind:
        case DocumentContentType.PARAGRAPH:
            return paragraph_translation_strategy
        case DocumentContentType.BULLET_LIST:
            return bullet_list_translation_strategy
        case DocumentContentType.CODE:
            return code_block_translation_strategy
        case DocumentContentType.TABLE:
            return table_translation_strategy


def _create_built_section(
    input: SectionWithInstruction,
    translation: SectionTranslationDefinition | None = None,
) -> BuiltSection:
    if translation is None:
        return BuiltSection(section=input.section, translation=SectionNoTranslation())
    return BuiltSection(
        section=input.section,
        translation=SectionTranslationInstruction(
            translation_instruction=input.translation_instruction,
            translation_strategies=tuple(
                _get_translation_strategy(content) for content in input.section.contents
            ),
        ),
    )


def build_sections[TSectionId: str, TContext: DocumentBaseContext](
    context: TContext,
    builders: tuple[SectionBuilder[TSectionId, TContext], ...],
    option: ConceptOption | None = None,
) -> Result[tuple[BuiltSection, ...], DocumentBuilderError]:

    sections: list[BuiltSection] = []
    for builder in builders:
        enabled = builder.enabled(context)
        if not enabled:
            continue
        section_with_instruction_result = builder.build(context, option)
        if isinstance(section_with_instruction_result, Failure):
            return section_with_instruction_result
        sections.append(
            _create_built_section(
                section_with_instruction_result.unwrap(), builder.translation
            )
        )

    return Success(tuple(sections))
