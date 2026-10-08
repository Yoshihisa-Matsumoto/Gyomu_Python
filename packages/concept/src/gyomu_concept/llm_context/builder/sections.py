from gyomu_schema.schemas.concept.llm_context.input import LlmContextBuildContext
from gyomu_schema.schemas.concept.llm_context.types import LlmContextSectionId

from gyomu_concept.document.builder.section import SectionBuilder
from gyomu_concept.llm_context.builder.section.architecture import build_architecture
from gyomu_concept.llm_context.builder.section.design_principles import (
    build_design_principles,
)
from gyomu_concept.llm_context.builder.section.editing_rule import build_editing_rules
from gyomu_concept.llm_context.builder.section.important_constraints import (
    build_important_constraints,
)
from gyomu_concept.llm_context.builder.section.navigation import build_navigation
from gyomu_concept.llm_context.builder.section.overview import build_overview
from gyomu_concept.llm_context.builder.section.package_responsibilities import (
    build_package_responsibilities,
)

LLMCONTEXT_SECTION_BUILDERS: tuple[
    SectionBuilder[LlmContextSectionId, LlmContextBuildContext], ...
] = (
    build_overview,  # paragraph + AI
    build_package_responsibilities,  # bullet-list
    build_architecture,  # paragraph + AI
    build_design_principles,  # bullet-list + AI buildSectionObject
    build_important_constraints,  # paragraph + AI
    build_editing_rules,  # bullet-list + AI buildSectionObject
    build_navigation,  # paragraph
)
