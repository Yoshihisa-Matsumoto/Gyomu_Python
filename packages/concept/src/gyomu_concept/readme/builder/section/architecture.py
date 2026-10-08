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

_section_id: ReadmeSectionId = "architecture"
"""Identifier for the architecture section."""


async def _build(
    context: DocumentBaseContext[Knowledge], option: ConceptOption | None = None
) -> Result[SectionWithInstruction[ReadmeSectionId], DocumentBuilderError]:
    """Builds the architecture section for the readme.

    Args:
        context (DocumentBaseContext): Document base context.
        option (ConceptOption | None): Optional concept options.

    Returns:
        Result[SectionWithInstruction[ReadmeSectionId], DocumentBuilderError]: Result
            containing the built section with instruction or a document builder error.
    """

    architecture_result = await build_section_item(
        _section_id, context, readme_prompt_provider
    )
    if isinstance(architecture_result, Failure):
        return architecture_result.alt(
            lambda error: DocumentBuilderError(
                "fail to build architecture",
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
                contents=(Paragraph(text=architecture_result.unwrap()),),
            )
        )
    )


def _enabled(_: DocumentBaseContext[Knowledge]) -> bool:
    """Determines whether the architecture section is enabled.

    Args:
        _ (DocumentBaseContext): Document base context.

    Returns:
        bool: True if enabled, False otherwise.
    """
    return True


build_architecture: SectionBuilder[ReadmeSectionId, DocumentBaseContext[Knowledge]] = (
    SectionBuilder[ReadmeSectionId, DocumentBaseContext[Knowledge]](
        id=_section_id,
        translation=SectionTranslationInstruction(translation_strategies=()),
        enabled=_enabled,
        build=_build,
    )
)
"""Section builder for the architecture readme section."""
