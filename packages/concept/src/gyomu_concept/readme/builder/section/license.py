from gyomu_concept.document.builder.section import SectionBuilder
from gyomu_concept.error.document import DocumentBuilderError
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.base import DocumentBaseContext
from gyomu_schema.schemas.concept.readme.types import ReadmeSectionId
from gyomu_schema.schemas.document.content import Paragraph
from gyomu_schema.schemas.document.section import (
    Section,
    SectionNoTranslation,
    SectionWithInstruction,
)
from returns.result import Result, Success

_section_id: ReadmeSectionId = "license"


async def _build(
    context: DocumentBaseContext, option: ConceptOption | None = None
) -> Result[SectionWithInstruction[ReadmeSectionId], DocumentBuilderError]:

    return Success(
        SectionWithInstruction[ReadmeSectionId](
            section=Section[ReadmeSectionId](
                id=_section_id,
                contents=(Paragraph(text=context.analysis.package.license),),
            )
        )
    )


def _enabled(_: DocumentBaseContext) -> bool:
    return True


build_license: SectionBuilder[ReadmeSectionId, DocumentBaseContext] = SectionBuilder[
    ReadmeSectionId, DocumentBaseContext
](
    id=_section_id,
    translation=SectionNoTranslation(),
    enabled=_enabled,
    build=_build,
)
