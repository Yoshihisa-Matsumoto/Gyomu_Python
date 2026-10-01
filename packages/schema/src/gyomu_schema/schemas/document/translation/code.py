from returns.result import Result, Success

from gyomu_schema.error.translation import TranslationError
from gyomu_schema.schemas.document.content import CodeBlock
from gyomu_schema.schemas.document.definition.code import code_block_definition
from gyomu_schema.schemas.document.section import (
    DocumentContentTranslationStrategy,
    RetryContextArg,
    TranslationState,
)


def _update_codeblock_retry_context(
    args: RetryContextArg[CodeBlock],
) -> Result[TranslationState[CodeBlock], TranslationError]:
    return Success(
        TranslationState[CodeBlock](
            context=args.original_context, validation=args.current_validation
        )
    )


code_block_translation_strategy = DocumentContentTranslationStrategy[CodeBlock](
    definition=code_block_definition,
    retry_context_updater=_update_codeblock_retry_context,
)
