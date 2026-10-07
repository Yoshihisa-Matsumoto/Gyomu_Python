from returns.result import Result, Success

from gyomu_schema.error.translation import TranslationError
from gyomu_schema.schemas.document.content import Table
from gyomu_schema.schemas.document.definition.table import table_definition
from gyomu_schema.schemas.document.section import (
    DocumentContentTranslationStrategy,
    RetryContextArg,
    TranslationState,
)


def _update_table_retry_context(
    args: RetryContextArg[Table],
) -> Result[TranslationState[Table], TranslationError]:
    """Update the retry context for table translation.

    Updates the retry context for a table translation.

    Args:
        args (RetryContextArg[Table]): The retry context arguments containing the
            original context and current validation.

    Returns:
        Result[TranslationState[Table], TranslationError]: A Result containing the
            updated TranslationState or a TranslationError.
    """
    return Success(
        TranslationState[Table](
            context=args.original_context, validation=args.current_validation
        )
    )


table_translation_strategy = DocumentContentTranslationStrategy[Table](
    definition=table_definition, retry_context_updater=_update_table_retry_context
)
"""Translation strategy for table content.

Translation strategy for table document content.
"""
