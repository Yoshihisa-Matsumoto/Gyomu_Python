from gyomu_ai_compiler.pipelines.document.executor.item import build_section_item
from gyomu_ai_compiler.pipelines.llm_context.prompt import llm_context_prompt_provider
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.llm_context.input import LlmContextBuildContext
from gyomu_schema.schemas.concept.llm_context.types import LlmContextSectionId
from gyomu_schema.schemas.document.content import Paragraph
from gyomu_schema.schemas.document.section import (
    Section,
    SectionNoTranslation,
    SectionWithInstruction,
)
from gyomu_schema.utility.context import caller_context
from returns.result import Failure, Result, Success

from gyomu_concept.document.builder.section import SectionBuilder
from gyomu_concept.error.document import DocumentBuilderError

_section_id: LlmContextSectionId = "overview"
"""Internal section identifier for the overview section."""


async def _build(
    context: LlmContextBuildContext, option: ConceptOption | None = None
) -> Result[SectionWithInstruction[LlmContextSectionId], DocumentBuilderError]:
    """Build the overview section for the LLM context.

    Builds the overview section for the LLM context.

    Args:
        context (LlmContextBuildContext): The LLM context build context.
        option (ConceptOption | None): Optional concept options.

    Returns:
        Result[SectionWithInstruction[LlmContextSectionId], DocumentBuilderError]: A
            Result containing the built overview section or a DocumentBuilderError on
            failure.
    """

    overview_result = await build_section_item(
        _section_id, context, llm_context_prompt_provider
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
        SectionWithInstruction[LlmContextSectionId](
            section=Section[LlmContextSectionId](
                id=_section_id, contents=(Paragraph(text=overview_result.unwrap()),)
            )
        )
    )


def _enabled(context: LlmContextBuildContext) -> bool:
    """Check if the overview section is enabled.

    Determines whether the overview section is enabled.

    Args:
        context (LlmContextBuildContext): The LLM context build context.

    Returns:
        bool: True if the section is enabled, False otherwise.
    """
    return True


build_overview: SectionBuilder[LlmContextSectionId, LlmContextBuildContext] = (
    SectionBuilder[LlmContextSectionId, LlmContextBuildContext](
        id=_section_id,
        translation=SectionNoTranslation(),
        enabled=_enabled,
        build=_build,
    )
)
"""Section builder for the overview section.

Section builder configuration for the overview section.
"""
