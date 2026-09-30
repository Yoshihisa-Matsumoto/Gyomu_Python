from gyomu_schema.error.translation import TranslationError
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.document.content import DocumentContent
from gyomu_schema.schemas.document.section import (
    BuiltSection,
    Section,
    SectionTranslationInstruction,
)
from gyomu_schema.schemas.document.translation import LanguageCodes
from returns.result import Result, Success


def translate_section(
    section: BuiltSection, language: LanguageCodes, option: ConceptOption | None = None
) -> Result[Section, TranslationError]:
    contents: list[DocumentContent] = []
    for index, content in enumerate(section.section.contents):
        if not isinstance(section.translation, SectionTranslationInstruction):
            contents.append(content)
        else:
            content_strategy = section.translation.translation_strategies[index]
            # translated_result =  execute_document_content_translation();

    return Success(
        Section(
            contents=tuple(contents), id=section.section.id, title=section.section.title
        )
    )
