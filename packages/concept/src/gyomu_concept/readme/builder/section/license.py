from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.base import DocumentBaseContext
from gyomu_schema.schemas.concept.readme.types import ReadmeSectionId
from gyomu_schema.schemas.document.content import Paragraph
from gyomu_schema.schemas.document.section import (
    Section,
    SectionNoTranslation,
    SectionWithInstruction,
)
from returns.result import Result, Success

from gyomu_concept.document.builder.section import SectionBuilder
from gyomu_concept.error.document import DocumentBuilderError

_section_id: ReadmeSectionId = "license"
"""Defines the section identifier for the license section."""


async def _build(
    context: DocumentBaseContext, option: ConceptOption | None = None
) -> Result[SectionWithInstruction[ReadmeSectionId], DocumentBuilderError]:
    """Builds the license section for the readme.

    Args:
        context (DocumentBaseContext): The document base context.
        option (ConceptOption | None): Optional concept options.

    Returns:
        Result[SectionWithInstruction[ReadmeSectionId], DocumentBuilderError]: A Result
            containing the section with instruction or a DocumentBuilderError.
    """

    return Success(
        SectionWithInstruction[ReadmeSectionId](
            section=Section[ReadmeSectionId](
                id=_section_id,
                contents=(Paragraph(text=context.analysis.package.license),),
            )
        )
    )


def _enabled(_: DocumentBaseContext) -> bool:
    """Determines whether the license section is enabled.

    Args:
        _ (DocumentBaseContext): The document base context.

    Returns:
        bool: True if enabled, false otherwise.
    """
    return True


build_license: SectionBuilder[ReadmeSectionId, DocumentBaseContext] = SectionBuilder[
    ReadmeSectionId, DocumentBaseContext
](
    id=_section_id,
    translation=SectionNoTranslation(),
    enabled=_enabled,
    build=_build,
)
"""Section builder for the license section."""
