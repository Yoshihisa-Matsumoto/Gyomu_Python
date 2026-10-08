from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.llm_context.input import LlmContextBuildContext
from gyomu_schema.schemas.concept.llm_context.types import LlmContextSectionId
from gyomu_schema.schemas.document.content import BulletList, BulletListItem
from gyomu_schema.schemas.document.section import (
    Section,
    SectionNoTranslation,
    SectionWithInstruction,
)
from returns.result import Result, Success

from gyomu_concept.document.builder.section import SectionBuilder
from gyomu_concept.error.document import DocumentBuilderError

_section_id: LlmContextSectionId = "package-responsibilities"


async def _build(
    context: LlmContextBuildContext, option: ConceptOption | None = None
) -> Result[SectionWithInstruction[LlmContextSectionId], DocumentBuilderError]:

    return Success(
        SectionWithInstruction[LlmContextSectionId](
            section=Section[LlmContextSectionId](
                id=_section_id,
                contents=(
                    BulletList(
                        items=tuple(
                            BulletListItem(translation_id=index, text=responsibility)
                            for index, responsibility in enumerate(
                                context.concept.responsibilities
                            )
                        )
                    ),
                ),
            )
        )
    )


def _enabled(_: LlmContextBuildContext) -> bool:

    return True


build_package_responsibilities: SectionBuilder[
    LlmContextSectionId, LlmContextBuildContext
] = SectionBuilder[LlmContextSectionId, LlmContextBuildContext](
    id=_section_id,
    translation=SectionNoTranslation(),
    enabled=_enabled,
    build=_build,
)
