from returns.result import Result, Success

from gyomu_schema.error.translation import TranslationError
from gyomu_schema.schemas.document.content import Paragraph
from gyomu_schema.schemas.document.definition.paragraph import paragraph_definition
from gyomu_schema.schemas.document.section import (
    DocumentContentTranslationStrategy,
    RetryContextArg,
    TranslationState,
)


def _update_paragraph_retry_context(
    args: RetryContextArg[Paragraph],
) -> Result[TranslationState[Paragraph], TranslationError]:
    return Success(
        TranslationState[Paragraph](
            context=args.original_context, validation=args.current_validation
        )
    )


paragraph_translation_strategy = DocumentContentTranslationStrategy[Paragraph](
    definition=paragraph_definition,
    retry_context_updater=_update_paragraph_retry_context,
)
