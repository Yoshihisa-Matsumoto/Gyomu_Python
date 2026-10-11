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

_section_id: LlmContextSectionId = "important-constraints"
"""Identifier for the important constraints section."""


async def _build(
    context: LlmContextBuildContext, option: ConceptOption | None = None
) -> Result[SectionWithInstruction[LlmContextSectionId], DocumentBuilderError]:
    """Builds the important constraints section for the LLM context.

    Args:
        context (LlmContextBuildContext): The build context for the LLM context.
        option (ConceptOption | None): Optional concept option configuration.

    Returns:
        Result[SectionWithInstruction[LlmContextSectionId], DocumentBuilderError]: A
            result containing the section with instructions or a DocumentBuilderError.
    """

    important_constraints_result = await build_section_item(
        _section_id, context, llm_context_prompt_provider
    )
    if isinstance(important_constraints_result, Failure):
        return important_constraints_result.alt(
            lambda error: DocumentBuilderError(
                "fail to build important-constraints",
                package_name=context.analysis.package.name,
                phase="section-build",
                section_id=_section_id,
                context=caller_context(),
            ).chain(error)
        )
    return Success(
        SectionWithInstruction[LlmContextSectionId](
            section=Section[LlmContextSectionId](
                id=_section_id,
                contents=(Paragraph(text=important_constraints_result.unwrap()),),
            )
        )
    )


def _enabled(context: LlmContextBuildContext) -> bool:
    """Checks whether the important constraints section is enabled.

    Args:
        context (LlmContextBuildContext): The build context for the LLM context.

    Returns:
        bool: True if the section is enabled, otherwise false.
    """
    return True


build_important_constraints: SectionBuilder[
    LlmContextSectionId, LlmContextBuildContext
] = SectionBuilder[LlmContextSectionId, LlmContextBuildContext](
    id=_section_id,
    translation=SectionNoTranslation(),
    enabled=_enabled,
    build=_build,
)
"""Section builder for the important constraints section."""
