from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.base import DocumentBaseContext, Knowledge
from gyomu_schema.schemas.concept.readme.types import ReadmeSectionId
from gyomu_schema.schemas.document.content import (
    BulletList,
    BulletListItem,
)
from gyomu_schema.schemas.document.section import (
    Section,
    SectionTranslationInstruction,
    SectionWithInstruction,
)
from returns.result import Result, Success

from gyomu_concept.document.builder.section import SectionBuilder
from gyomu_concept.error.document import DocumentBuilderError

_section_id: ReadmeSectionId = "public-api"
"""Readme section identifier for the public API."""


async def _build(
    context: DocumentBaseContext[Knowledge], option: ConceptOption | None = None
) -> Result[SectionWithInstruction[ReadmeSectionId], DocumentBuilderError]:
    """Builds the public API readme section from the document context.

    Args:
        context (DocumentBaseContext): Document base context containing concept
            information.
        option (ConceptOption | None): Optional concept builder options.

    Returns:
        Result[SectionWithInstruction[ReadmeSectionId], DocumentBuilderError]: A Result
            containing the built section with instruction or a DocumentBuilderError.
    """

    return Success(
        SectionWithInstruction[ReadmeSectionId](
            section=Section[ReadmeSectionId](
                id=_section_id,
                contents=(
                    BulletList(
                        items=tuple(
                            BulletListItem(
                                translation_id=index,
                                text=f"{item.name} - {item.description}",
                            )
                            for index, item in enumerate(context.concept.capabilities)
                        )
                    ),
                ),
            )
        )
    )


def _enabled(_: DocumentBaseContext[Knowledge]) -> bool:
    """Determines whether the public API section is enabled.

    Args:
        _ (DocumentBaseContext): Document base context.

    Returns:
        bool: Always returns True.
    """
    return True


build_public_api: SectionBuilder[ReadmeSectionId, DocumentBaseContext[Knowledge]] = (
    SectionBuilder[ReadmeSectionId, DocumentBaseContext[Knowledge]](
        id=_section_id,
        translation=SectionTranslationInstruction(translation_strategies=()),
        enabled=_enabled,
        build=_build,
    )
)
"""Section builder for the public API readme section."""
