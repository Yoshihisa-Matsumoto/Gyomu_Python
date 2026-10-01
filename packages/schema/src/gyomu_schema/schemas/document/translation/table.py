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
    return Success(
        TranslationState[Table](
            context=args.original_context, validation=args.current_validation
        )
    )


table_translation_strategy = DocumentContentTranslationStrategy[Table](
    definition=table_definition, retry_context_updater=_update_table_retry_context
)
