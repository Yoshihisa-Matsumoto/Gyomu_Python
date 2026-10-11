from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.llm_context.input import LlmContextBuildContext
from gyomu_schema.schemas.concept.llm_context.types import LlmContextSectionId
from gyomu_schema.schemas.document.content import BulletList, BulletListItem
from gyomu_schema.schemas.document.section import (
    Section,
    SectionNoTranslation,
    SectionWithInstruction,
)
from returns.result import Result, Success

from gyomu_concept.document.builder.section import SectionBuilder
from gyomu_concept.error.document import DocumentBuilderError

_section_id: LlmContextSectionId = "package-responsibilities"
"""Internal section ID for package responsibilities."""


async def _build(
    context: LlmContextBuildContext, option: ConceptOption | None = None
) -> Result[SectionWithInstruction[LlmContextSectionId], DocumentBuilderError]:
    """Builds the package responsibilities section containing a bullet list of
    responsibilities.

    Args:
        context (LlmContextBuildContext): Build context containing the concept
            responsibilities.
        option (ConceptOption | None): Optional concept options.

    Returns:
        Result[SectionWithInstruction[LlmContextSectionId], DocumentBuilderError]: A
            result containing the section with instructions or a document builder error.
    """

    return Success(
        SectionWithInstruction[LlmContextSectionId](
            section=Section[LlmContextSectionId](
                id=_section_id,
                contents=(
                    BulletList(
                        items=tuple(
                            BulletListItem(translation_id=index, text=responsibility)
                            for index, responsibility in enumerate(
                                context.concept.responsibilities
                            )
                        )
                    ),
                ),
            )
        )
    )


def _enabled(_: LlmContextBuildContext) -> bool:
    """Determines whether the package responsibilities section is enabled.

    Args:
        _ (LlmContextBuildContext): Build context.

    Returns:
        bool: True if enabled.
    """

    return True


build_package_responsibilities: SectionBuilder[
    LlmContextSectionId, LlmContextBuildContext
] = SectionBuilder[LlmContextSectionId, LlmContextBuildContext](
    id=_section_id,
    translation=SectionNoTranslation(),
    enabled=_enabled,
    build=_build,
)
"""Section builder for package responsibilities."""
