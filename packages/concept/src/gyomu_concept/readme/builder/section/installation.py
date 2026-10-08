from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.base import DocumentBaseContext, Knowledge
from gyomu_schema.schemas.concept.readme.types import ReadmeSectionId
from gyomu_schema.schemas.document.content import CodeBlock, Paragraph
from gyomu_schema.schemas.document.section import (
    Section,
    SectionTranslationInstruction,
    SectionWithInstruction,
)
from returns.result import Result, Success

from gyomu_concept.document.builder.section import SectionBuilder
from gyomu_concept.error.document import DocumentBuilderError

_section_id: ReadmeSectionId = "installation"
"""Section identifier for the installation section."""


async def _build(
    context: DocumentBaseContext[Knowledge], option: ConceptOption | None = None
) -> Result[SectionWithInstruction[ReadmeSectionId], DocumentBuilderError]:
    """Build the installation section of the README.

    Args:
        context (DocumentBaseContext): The document base context.
        option (ConceptOption | None): Optional concept options.

    Returns:
        Result[SectionWithInstruction[ReadmeSectionId], DocumentBuilderError]: Result
            containing the SectionWithInstruction for the installation section or a
            DocumentBuilderError.
    """

    return Success(
        SectionWithInstruction[ReadmeSectionId](
            section=Section[ReadmeSectionId](
                id=_section_id,
                contents=(
                    Paragraph(text="Install using uv."),
                    CodeBlock(
                        language="bash", code=f"uv add {context.analysis.package.name}"
                    ),
                ),
            )
        )
    )


def _enabled(_: DocumentBaseContext[Knowledge]) -> bool:
    """Check whether the installation section is enabled.

    Args:
        _ (DocumentBaseContext): The document base context.

    Returns:
        bool: True if the section is enabled, false otherwise.
    """
    return True


build_installation: SectionBuilder[ReadmeSectionId, DocumentBaseContext[Knowledge]] = (
    SectionBuilder[ReadmeSectionId, DocumentBaseContext[Knowledge]](
        id=_section_id,
        translation=SectionTranslationInstruction(translation_strategies=()),
        enabled=_enabled,
        build=_build,
    )
)
"""Section builder for the installation section."""
