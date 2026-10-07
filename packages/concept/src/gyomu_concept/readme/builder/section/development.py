from gyomu_ai_compiler.pipelines.document.executor.item import build_section_item
from gyomu_ai_compiler.pipelines.readme.prompt import readme_prompt_provider
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.base import DocumentBaseContext
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

_section_id: ReadmeSectionId = "development"
"""Internal section ID for the development readme section."""


async def _build(
    context: DocumentBaseContext, option: ConceptOption | None = None
) -> Result[SectionWithInstruction[ReadmeSectionId], DocumentBuilderError]:
    """Builds the development section for the readme.

    Args:
        context (DocumentBaseContext): The document base context.
        option (ConceptOption | None): Optional concept options.

    Returns:
        Result[SectionWithInstruction[ReadmeSectionId], DocumentBuilderError]: A Result
            containing the section with instructions or a document builder error.
    """

    development_result = await build_section_item(
        _section_id, context, readme_prompt_provider
    )
    if isinstance(development_result, Failure):
        return development_result.alt(
            lambda error: DocumentBuilderError(
                "fail to build development",
                package_name=context.analysis.package.name,
                phase="section-build",
                section_id=_section_id,
                context=caller_context(),
            ).chain(error)
        )
    return Success(
        SectionWithInstruction[ReadmeSectionId](
            section=Section[ReadmeSectionId](
                id=_section_id,
                contents=(Paragraph(text=development_result.unwrap()),),
            )
        )
    )


def _enabled(_: DocumentBaseContext) -> bool:
    """Determines whether the development section is enabled.

    Args:
        _ (DocumentBaseContext): The document base context.

    Returns:
        bool: True if enabled.
    """
    return True


build_development: SectionBuilder[ReadmeSectionId, DocumentBaseContext] = (
    SectionBuilder[ReadmeSectionId, DocumentBaseContext](
        id=_section_id,
        translation=SectionTranslationInstruction(translation_strategies=()),
        enabled=_enabled,
        build=_build,
    )
)
"""Section builder for the development section of the readme."""
