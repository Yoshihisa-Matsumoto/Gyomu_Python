from gyomu_ai_compiler.pipelines.llm_context.prompt import llm_context_prompt_provider
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.llm_context.input import LlmContextBuildContext
from gyomu_schema.schemas.concept.llm_context.types import LlmContextSectionId
from gyomu_schema.schemas.document.section import (
    Section,
    SectionNoTranslation,
    SectionWithInstruction,
)
from returns.result import Failure, Result, Success

from gyomu_concept.document.builder.bullet_list import build_bullet_list
from gyomu_concept.document.builder.section import SectionBuilder
from gyomu_concept.error.document import DocumentBuilderError

_section_id: LlmContextSectionId = "design-principles"
"""Section ID for design principles."""


async def _build(
    context: LlmContextBuildContext, option: ConceptOption | None = None
) -> Result[SectionWithInstruction[LlmContextSectionId], DocumentBuilderError]:
    """Builds the design principles section.

    Args:
        context (LlmContextBuildContext): LLM context build context
        option (ConceptOption | None): Optional concept option

    Returns:
        Result[SectionWithInstruction[LlmContextSectionId], DocumentBuilderError]:
            Result containing the section with instruction or a document builder error
    """

    desing_principles_result = await build_bullet_list(
        _section_id, context, llm_context_prompt_provider
    )
    if isinstance(desing_principles_result, Failure):
        return desing_principles_result.alt(
            lambda error: DocumentBuilderError(
                "fail to build design principles",
                package_name=context.analysis.package.name,
                phase="section-build",
                section_id=_section_id,
            ).chain(error)
        )
    return Success(
        SectionWithInstruction[LlmContextSectionId](
            section=Section[LlmContextSectionId](
                id=_section_id,
                contents=(desing_principles_result.unwrap(),),
            )
        )
    )


def _enabled(_: LlmContextBuildContext) -> bool:
    """Checks whether the design principles section is enabled.

    Args:
        _ (LlmContextBuildContext): LLM context build context

    Returns:
        bool: Always returns True
    """

    return True


build_design_principles: SectionBuilder[LlmContextSectionId, LlmContextBuildContext] = (
    SectionBuilder[LlmContextSectionId, LlmContextBuildContext](
        id=_section_id,
        translation=SectionNoTranslation(),
        enabled=_enabled,
        build=_build,
    )
)
"""Section builder for the design principles section."""
