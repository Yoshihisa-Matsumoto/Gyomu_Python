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
from gyomu_ai_compiler.pipelines.llm_context.renderer.section import (
    LLM_CONTEXT_SECTION_PROMPT_MAP,
)


def test_llm_context_llm_section_prompt_map() -> None:
    assert {
        "overview": build_overview_messages,
        "architecture": build_architecture_messages,
        "design-principles": build_design_principles_messages,
        "important-constraints": build_important_constraints_messages,
        "editing-rules": build_editing_rule_messages,
    } == LLM_CONTEXT_SECTION_PROMPT_MAP
