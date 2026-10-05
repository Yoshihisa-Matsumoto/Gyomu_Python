from gyomu_ai_compiler.pipelines.translation.executor.content import (
    execute_document_content_translation,
)
from gyomu_schema.error.translation import TranslationError
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.document.content import DocumentContent
from gyomu_schema.schemas.document.section import (
    BuiltSection,
    LanguageCodes,
    Section,
    SectionTranslationInstruction,
)
from returns.result import Failure, Result, Success


async def translate_section[TSectionId: str](
    section: BuiltSection[TSectionId],
    language: LanguageCodes,
    option: ConceptOption | None = None,
) -> Result[Section[TSectionId], TranslationError]:
    contents: list[DocumentContent] = []
    for index, content in enumerate(section.section.contents):
        if not isinstance(section.translation, SectionTranslationInstruction):
            contents.append(content)
        else:
            content_strategy = section.translation.translation_strategies[index]
            translated_result = await execute_document_content_translation(
                language=language,
                section_id=section.section.id,
                context=content,
                section_definition=section.translation,
                content_strategy=content_strategy,
            )
            if isinstance(translated_result, Failure):
                return translated_result
            contents.append(translated_result.unwrap())

    return Success(
        Section(
            contents=tuple(contents), id=section.section.id, title=section.section.title
        )
    )
