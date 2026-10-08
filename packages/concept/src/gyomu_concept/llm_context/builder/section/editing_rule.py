from gyomu_ai_compiler.pipelines.llm_context.prompt import llm_context_prompt_provider
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.llm_context.input import LlmContextBuildContext
from gyomu_schema.schemas.concept.llm_context.types import LlmContextSectionId
from gyomu_schema.schemas.document.section import (
    Section,
    SectionNoTranslation,
    SectionWithInstruction,
)
from gyomu_schema.utility.context import caller_context
from returns.result import Failure, Result, Success

from gyomu_concept.document.builder.bullet_list import build_bullet_list
from gyomu_concept.document.builder.section import SectionBuilder
from gyomu_concept.error.document import DocumentBuilderError

_section_id: LlmContextSectionId = "editing-rules"


async def _build(
    context: LlmContextBuildContext, option: ConceptOption | None = None
) -> Result[SectionWithInstruction[LlmContextSectionId], DocumentBuilderError]:

    editing_rules_result = await build_bullet_list(
        _section_id, context, llm_context_prompt_provider
    )
    if isinstance(editing_rules_result, Failure):
        return editing_rules_result.alt(
            lambda error: DocumentBuilderError(
                "fail to build editing rules",
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
                contents=(editing_rules_result.unwrap(),),
            )
        )
    )


def _enabled(_: LlmContextBuildContext) -> bool:

    return True


build_editing_rules: SectionBuilder[LlmContextSectionId, LlmContextBuildContext] = (
    SectionBuilder[LlmContextSectionId, LlmContextBuildContext](
        id=_section_id,
        translation=SectionNoTranslation(),
        enabled=_enabled,
        build=_build,
    )
)
