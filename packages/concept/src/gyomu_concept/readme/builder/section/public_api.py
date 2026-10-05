from gyomu_concept.document.builder.section import SectionBuilder
from gyomu_concept.error.document import DocumentBuilderError
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.base import DocumentBaseContext
from gyomu_schema.schemas.concept.readme.types import ReadmeSectionId
from gyomu_schema.schemas.document.content import (
    BulletList,
    BulletListItem,
)
from gyomu_schema.schemas.document.section import (
    Section,
    SectionTranslationInstruction,
    SectionWithInstruction,
)
from returns.result import Result, Success

_section_id: ReadmeSectionId = "public-api"


async def _build(
    context: DocumentBaseContext, option: ConceptOption | None = None
) -> Result[SectionWithInstruction[ReadmeSectionId], DocumentBuilderError]:

    return Success(
        SectionWithInstruction[ReadmeSectionId](
            section=Section[ReadmeSectionId](
                id=_section_id,
                contents=(
                    BulletList(
                        items=tuple(
                            BulletListItem(
                                translation_id=index,
                                text=f"{item.name} - {item.description}",
                            )
                            for index, item in enumerate(context.concept.capabilities)
                        )
                    ),
                ),
            )
        )
    )


def _enabled(_: DocumentBaseContext) -> bool:
    return True


build_public_api: SectionBuilder[ReadmeSectionId, DocumentBaseContext] = SectionBuilder[
    ReadmeSectionId, DocumentBaseContext
](
    id=_section_id,
    translation=SectionTranslationInstruction(translation_strategies=()),
    enabled=_enabled,
    build=_build,
)
