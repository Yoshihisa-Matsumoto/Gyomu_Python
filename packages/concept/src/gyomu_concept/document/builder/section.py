from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from gyomu_schema.option.concept import ConceptOption
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

from gyomu_concept.error.document import DocumentBuilderError


@dataclass
class SectionBuilder[TSectionId: str, TContext]:
    """Represents a builder for document sections with translation and enablement
    definitions.
    """

    id: TSectionId
    """Unique identifier of the section."""

    translation: SectionTranslationDefinition
    """Translation definition for the section."""

    build: Callable[
        [TContext, ConceptOption | None],
        Awaitable[Result[SectionWithInstruction[TSectionId], DocumentBuilderError]],
    ]
    """Callable to build the section with context and options."""

    enabled: Callable[[TContext], bool]
    """Callable to determine whether the section is enabled based on context."""


def _get_translation_strategy(
    content: DocumentContent,
) -> DocumentContentTranslationStrategy[Any]:
    """Retrieves the appropriate translation strategy for a given document content type.

    Args:
        content (DocumentContent): Document content to get the strategy for

    Returns:
        DocumentContentTranslationStrategy[Any]: Translation strategy corresponding to
            the content kind
    """
    match content.kind:
        case DocumentContentType.PARAGRAPH:
            return paragraph_translation_strategy
        case DocumentContentType.BULLET_LIST:
            return bullet_list_translation_strategy
        case DocumentContentType.CODE:
            return code_block_translation_strategy
        case DocumentContentType.TABLE:
            return table_translation_strategy


def _create_built_section[TSectionId: str](
    input: SectionWithInstruction[TSectionId],
    translation: SectionTranslationDefinition,
) -> BuiltSection[TSectionId]:
    """Creates a built section from an input section with instruction and translation
    definition.

    Args:
        input (SectionWithInstruction[TSectionId]): Section with instruction input
        translation (SectionTranslationDefinition): Translation definition for the
            section

    Returns:
        BuiltSection[TSectionId]: Constructed built section instance
    """
    if isinstance(translation, SectionNoTranslation):
        return BuiltSection(section=input.section, translation=translation)
    return BuiltSection(
        section=input.section,
        translation=SectionTranslationInstruction(
            translation_instruction=input.translation_instruction,
            translation_strategies=tuple(
                _get_translation_strategy(content) for content in input.section.contents
            ),
        ),
    )


async def build_sections[TSectionId: str, TContext](
    context: TContext,
    builders: tuple[SectionBuilder[TSectionId, TContext], ...],
    option: ConceptOption | None = None,
) -> Result[tuple[BuiltSection[TSectionId], ...], DocumentBuilderError]:
    """Builds all enabled sections using the provided section builders.

    Args:
        context (TContext): Context used by the section builders
        builders (tuple[SectionBuilder[TSectionId, TContext], ...]): Tuple of section
            builders to execute
        option (ConceptOption | None): Optional concept options

    Returns:
        Result[tuple[BuiltSection[TSectionId], ...], DocumentBuilderError]: Result
            containing a tuple of built sections or a document builder error
    """

    sections: list[BuiltSection[TSectionId]] = []
    for builder in builders:
        enabled = builder.enabled(context)
        if not enabled:
            continue
        section_with_instruction_result = await builder.build(context, option)
        if isinstance(section_with_instruction_result, Failure):
            return section_with_instruction_result
        sections.append(
            _create_built_section(
                section_with_instruction_result.unwrap(), builder.translation
            )
        )

    return Success(tuple(sections))
