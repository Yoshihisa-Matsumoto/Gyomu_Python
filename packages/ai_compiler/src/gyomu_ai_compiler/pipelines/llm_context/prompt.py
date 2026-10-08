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

    return LLM_CONTEXT_SECTION_PROMPT_MAP[section_id](context)


llm_context_prompt_provider = SectionPromptProvider[
    LlmContextSectionId, LlmContextBuildContext
](render=_render)
