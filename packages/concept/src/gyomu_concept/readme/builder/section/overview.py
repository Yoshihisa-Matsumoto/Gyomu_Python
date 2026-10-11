from gyomu_ai_compiler.pipelines.document.executor.item import build_section_item
from gyomu_ai_compiler.pipelines.readme.prompt import readme_prompt_provider
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.base import DocumentBaseContext, Knowledge
from gyomu_schema.schemas.concept.readme.types import ReadmeSectionId
from gyomu_schema.schemas.document.content import Paragraph
from gyomu_schema.schemas.document.section import (
    Section,
    SectionTranslationInstruction,
    SectionWithInstruction,
)
from gyomu_schema.utility.context import caller_context
from returns.result import Failure, Result, Success

from gyomu_concept.document.builder.section import SectionBuilder
from gyomu_concept.error.document import DocumentBuilderError

_section_id: ReadmeSectionId = "overview"
"""Internal section identifier for the overview section."""


async def _build(
    context: DocumentBaseContext[Knowledge], option: ConceptOption | None = None
) -> Result[SectionWithInstruction[ReadmeSectionId], DocumentBuilderError]:
    """Builds the overview section for the README.

    Args:
        context (DocumentBaseContext): The base context for document building.
        option (ConceptOption | None): Optional concept configuration options.

    Returns:
        Result[SectionWithInstruction[ReadmeSectionId], DocumentBuilderError]: Result
            containing the built section with instructions or a document builder error.
    """
    overview_result = await build_section_item(
        _section_id, context, readme_prompt_provider
    )
    if isinstance(overview_result, Failure):
        return overview_result.alt(
            lambda error: DocumentBuilderError(
                "fail to build overview",
                package_name=context.analysis.package.name,
                phase="section-build",
                section_id=_section_id,
                context=caller_context(),
            ).chain(error)
        )
    return Success(
        SectionWithInstruction[ReadmeSectionId](
            section=Section[ReadmeSectionId](
                id=_section_id, contents=(Paragraph(text=overview_result.unwrap()),)
            )
        )
    )


def _enabled(context: DocumentBaseContext[Knowledge]) -> bool:
    """Determines whether the overview section is enabled.

    Args:
        context (DocumentBaseContext): The base context for document building.

    Returns:
        bool: True if the section is enabled.
    """
    return True


build_overview: SectionBuilder[ReadmeSectionId, DocumentBaseContext[Knowledge]] = (
    SectionBuilder[ReadmeSectionId, DocumentBaseContext[Knowledge]](
        id=_section_id,
        translation=SectionTranslationInstruction(translation_strategies=()),
        enabled=_enabled,
        build=_build,
    )
)
"""Section builder instance for the overview section."""
