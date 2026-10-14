from gyomu_ai_compiler.pipelines.document.executor.item import build_section_item
from gyomu_ai_compiler.pipelines.llm_context.prompt import llm_context_prompt_provider
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.llm_context.input import LlmContextBuildContext
from gyomu_schema.schemas.concept.llm_context.types import LlmContextSectionId
from gyomu_schema.schemas.document.content import paragraph_from_text
from gyomu_schema.schemas.document.section import (
    Section,
    SectionNoTranslation,
    SectionWithInstruction,
)
from gyomu_schema.utility.context import caller_context
from returns.result import Failure, Result, Success

from gyomu_concept.document.builder.section import SectionBuilder
from gyomu_concept.error.document import DocumentBuilderError

_section_id: LlmContextSectionId = "architecture"
"""Section ID for the architecture section."""


async def _build(
    context: LlmContextBuildContext, option: ConceptOption | None = None
) -> Result[SectionWithInstruction[LlmContextSectionId], DocumentBuilderError]:
    """Asynchronously builds the architecture section of the LLM context.

    Args:
        context (LlmContextBuildContext): The LLM context build context.
        option (ConceptOption | None): Optional concept options.

    Returns:
        Result[SectionWithInstruction[LlmContextSectionId], DocumentBuilderError]: A
            Result containing the built architecture section with instructions or a
            DocumentBuilderError.
    """

    architecture_result = await build_section_item(
        _section_id, context, llm_context_prompt_provider
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
        SectionWithInstruction[LlmContextSectionId](
            section=Section[LlmContextSectionId](
                id=_section_id,
                contents=(paragraph_from_text(text=architecture_result.unwrap()),),
            )
        )
    )


def _enabled(_: LlmContextBuildContext) -> bool:
    """Determines whether the architecture section is enabled.

    Args:
        _ (LlmContextBuildContext): The LLM context build context.

    Returns:
        bool: True if the section is enabled.
    """

    return True


build_architecture: SectionBuilder[LlmContextSectionId, LlmContextBuildContext] = (
    SectionBuilder[LlmContextSectionId, LlmContextBuildContext](
        id=_section_id,
        translation=SectionNoTranslation(),
        enabled=_enabled,
        build=_build,
    )
)
"""Section builder configuration for the architecture section."""
