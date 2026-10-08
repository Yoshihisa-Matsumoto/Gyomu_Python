from collections.abc import Callable, Mapping

from gyomu_schema.conversation.conversation import ConversationSchema
from gyomu_schema.error.io import GyomuIOError
from gyomu_schema.schemas.concept.llm_context.input import LlmContextBuildContext
from gyomu_schema.schemas.concept.llm_context.types import LlmContextSectionId
from returns.result import Result

from gyomu_ai_compiler.pipelines.llm_context.renderer.architecture import (
    build_architecture_messages,
)
from gyomu_ai_compiler.pipelines.llm_context.renderer.design_principles import (
    build_design_principles_messages,
)
from gyomu_ai_compiler.pipelines.llm_context.renderer.editing_rule import (
    build_editing_rule_messages,
)
from gyomu_ai_compiler.pipelines.llm_context.renderer.important_constraints import (
    build_important_constraints_messages,
)
from gyomu_ai_compiler.pipelines.llm_context.renderer.overview import (
    build_overview_messages,
)

LLM_CONTEXT_SECTION_PROMPT_MAP: Mapping[
    LlmContextSectionId,
    Callable[[LlmContextBuildContext], Result[ConversationSchema, GyomuIOError]],
] = {
    "overview": build_overview_messages,
    "architecture": build_architecture_messages,
    "design-principles": build_design_principles_messages,
    "important-constraints": build_important_constraints_messages,
    "editing-rules": build_editing_rule_messages,
}
