from dataclasses import dataclass

from gyomu_schema.error.translation import TranslationError
from gyomu_schema.schemas.document.content import DocumentContent
from gyomu_schema.schemas.document.section import (
    DocumentContentTranslationStrategy,
    LanguageCodes,
    SectionTranslationDefinition,
)
from gyomu_schema.schemas.document.validation import ValidationResult
from gyomu_schema.utility.context import caller_context
from returns.result import Failure, Result

from gyomu_ai_compiler.pipelines.translation.executor.merge import merge_retry_context
from gyomu_ai_compiler.pipelines.translation.executor.translate import (
    translate_document_content,
)

MAX_TRANSLATION_ATTEMPTS = 5
"""Maximum number of translation attempt retries allowed.

Maximum number of translation attempt retries allowed.
"""


async def execute_document_content_translation[TSchema: DocumentContent](
    language: LanguageCodes,
    section_id: str,
    context: TSchema,
    section_definition: SectionTranslationDefinition,
    content_strategy: DocumentContentTranslationStrategy[TSchema],
) -> Result[TSchema, TranslationError]:
    """Executes document content translation with retry support.

    Executes document content translation with automatic retry handling.

    Args:
        language (LanguageCodes): Target language for the translation
        section_id (str): Unique identifier of the section being translated
        context (TSchema): Document content context to be translated
        section_definition (SectionTranslationDefinition): Definition rules for section
            translation
        content_strategy (DocumentContentTranslationStrategy[TSchema]): Translation and
            content strategy handler

    Returns:
        Result[TSchema, TranslationError]: A Result containing the translated document
            content schema or a TranslationError
    """
    return await _retry_document_content_translation(
        language=language,
        section_id=section_id,
        context=context,
        section_definition=section_definition,
        content_strategy=content_strategy,
        max_attempt=MAX_TRANSLATION_ATTEMPTS,
    )


@dataclass
class TemporallyTranslationState[TSchema: DocumentContent]:
    """Temporary translation state dataclass holding context and validation results.

    Temporary state tracking container used during document content translation and
    retry reconciliation.
    """

    context: TSchema
    """The document content context.

    The document content context.
    """
    validation: ValidationResult | None
    """The current validation result or None.

    The current validation result or None.
    """


async def _retry_document_content_translation[TSchema: DocumentContent](
    language: LanguageCodes,
    section_id: str,
    context: TSchema,
    section_definition: SectionTranslationDefinition,
    content_strategy: DocumentContentTranslationStrategy[TSchema],
    max_attempt: int,
) -> Result[TSchema, TranslationError]:
    """Retries document content translation until successful or maximum attempts are
    reached.

    Internal helper to perform document content translation attempts up to a specified
    maximum count.

    Args:
        language (LanguageCodes): Target language code
        section_id (str): Unique section identifier
        context (TSchema): Document content context
        section_definition (SectionTranslationDefinition): Section translation
            definition rules
        content_strategy (DocumentContentTranslationStrategy[TSchema]): Content
            translation strategy instance
        max_attempt (int): Maximum number of attempts allowed

    Returns:
        Result[TSchema, TranslationError]: Result containing the translated schema or a
            TranslationError upon failure
    """
    attempt: int = 0
    current_validation: ValidationResult | None = None
    update_translation_state = TemporallyTranslationState[TSchema](
        context=context, validation=current_validation
    )

    while attempt < max_attempt:
        translate_result = await translate_document_content(
            language,
            section_id,
            update_translation_state.context,
            section_definition,
            content_strategy,
            update_translation_state.validation,
        )
        if isinstance(translate_result, Failure):
            return translate_result
        previous_validation = current_validation

        translated_context = translate_result.unwrap()
        current_validation = content_strategy.definition.reconciliation.validate(
            update_translation_state.context, translated_context
        )
        if current_validation.is_valid:
            return translate_result

        merge_result = merge_retry_context(
            section_id=section_id,
            section_definition=section_definition,
            content_strategy=content_strategy,
            current_validation=current_validation,
            previous_validation=previous_validation,
            original_context=update_translation_state.context,
            translated_context=translated_context,
        )
        if isinstance(merge_result, Failure):
            return merge_result
        state = merge_result.unwrap()
        update_translation_state = TemporallyTranslationState[TSchema](
            context=state.context, validation=state.validation
        )

        attempt += 1

    return Failure(
        TranslationError(
            message="translation failed with maximum retry",
            content_type=context.kind,
            phase="retry",
            section_id=section_id,
            context=caller_context(),
        )
    )
