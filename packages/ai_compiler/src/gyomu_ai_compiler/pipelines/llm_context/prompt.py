from gyomu_schema.conversation.conversation import ConversationSchema
from gyomu_schema.error.io import GyomuIOError
from gyomu_schema.schemas.concept.llm_context.input import LlmContextBuildContext
from gyomu_schema.schemas.concept.llm_context.types import LlmContextSectionId
from gyomu_schema.schemas.document.section import SectionPromptProvider
from returns.result import Result

from gyomu_ai_compiler.pipelines.llm_context.renderer.section import (
    LLM_CONTEXT_SECTION_PROMPT_MAP,
)


def _render(
    section_id: LlmContextSectionId, context: LlmContextBuildContext
) -> Result[ConversationSchema, GyomuIOError]:
    """Renders an LLM context section prompt.

    Renders a prompt for the specified LLM context section using the provided build
    context.

    Args:
        section_id (LlmContextSectionId): The identifier of the LLM context section.
        context (LlmContextBuildContext): The build context for the LLM context section.

    Returns:
        Result[ConversationSchema, GyomuIOError]: A Result containing the
            ConversationSchema upon success or GyomuIOError upon failure.
    """

    return LLM_CONTEXT_SECTION_PROMPT_MAP[section_id](context)


llm_context_prompt_provider = SectionPromptProvider[
    LlmContextSectionId, LlmContextBuildContext
](render=_render)
"""Prompt provider for LLM context sections.

Provider instance for rendering LLM context section prompts.
"""
