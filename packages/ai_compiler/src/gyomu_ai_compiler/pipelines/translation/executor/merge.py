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
    if current_validation.is_valid or (
        previous_validation is not None and previous_validation.is_valid
    ):
        return Failure(
            TranslationError(
                message="Invalid call. Should be called only when validation result fails",
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
