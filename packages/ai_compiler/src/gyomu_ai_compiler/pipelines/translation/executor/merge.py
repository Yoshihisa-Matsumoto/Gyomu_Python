from gyomu_schema.error.translation import TranslationError
from gyomu_schema.schemas.document.content import DocumentContent
from gyomu_schema.schemas.document.section import (
    DocumentContentTranslationStrategy,
    RetryContextArg,
    SectionTranslationDefinition,
    TranslationState,
)
from gyomu_schema.schemas.document.validation import ValidationResult
from gyomu_schema.utility.context import caller_context
from returns.result import Failure, Result


def merge_retry_context[TSchema: DocumentContent](
    section_id: str,
    section_definition: SectionTranslationDefinition,
    content_strategy: DocumentContentTranslationStrategy[TSchema],
    current_validation: ValidationResult,
    previous_validation: ValidationResult | None,
    original_context: TSchema,
    translated_context: TSchema,
) -> Result[TranslationState[TSchema], TranslationError]:
    """Merge retry context for a document section translation.

    Merges translation retry context using the content strategy when validation fails.

    Args:
        section_id (str): Identifier of the section.
        section_definition (SectionTranslationDefinition): Definition of the section
            translation.
        content_strategy (DocumentContentTranslationStrategy[TSchema]): Document content
            translation strategy.
        current_validation (ValidationResult): Current validation result.
        previous_validation (ValidationResult | None): Previous validation result, if
            any.
        original_context (TSchema): Original document context.
        translated_context (TSchema): Translated document context.

    Returns:
        Result[TranslationState[TSchema], TranslationError]: A Result containing the
            TranslationState or a TranslationError.
    """
    if current_validation.is_valid or (
        previous_validation is not None and previous_validation.is_valid
    ):
        return Failure(
            TranslationError(
                message=(
                    "Invalid call. Should be called only when validation result fails"
                ),
                content_type=original_context.kind,
                phase="retry-context",
                section_id=section_id,
                context=caller_context(),
            )
        )
    retry_arg = RetryContextArg[TSchema](
        section_id=section_id,
        section_definition=section_definition,
        current_validation=current_validation,
        previous_validation=previous_validation,
        original_context=original_context,
        translated_context=translated_context,
    )
    return content_strategy.retry_context_updater(retry_arg)
