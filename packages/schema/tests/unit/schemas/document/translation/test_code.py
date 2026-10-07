from gyomu_schema.schemas.document.content import CodeBlock
from gyomu_schema.schemas.document.section import RetryContextArg, SectionNoTranslation
from gyomu_schema.schemas.document.translation.code import (
    _update_codeblock_retry_context,
)
from returns.result import Success

from packages.schema.schema_test_support.concept_helpers import (
    create_codeblock,
    create_validation_result,
)


def test_update_retry_context_returns_original_context_and_validation() -> None:
    original_context = create_codeblock("This is a pen.")
    current_validation = create_validation_result()

    result = _update_codeblock_retry_context(
        RetryContextArg[CodeBlock](
            section_id="section-1",
            section_definition=SectionNoTranslation(),
            original_context=original_context,
            translated_context=create_codeblock("これはペンです。"),
            current_validation=current_validation,
            previous_validation=None,
        )
    )

    assert isinstance(result, Success)

    state = result.unwrap()
    assert state.context is original_context
    assert state.validation is current_validation


def test_update_retry_context_does_not_use_translated_context() -> None:
    original_context = create_codeblock("This is a pen.")
    translated_context = create_codeblock("これはペンです。")
    current_validation = create_validation_result()

    result = _update_codeblock_retry_context(
        RetryContextArg[CodeBlock](
            section_id="section-1",
            section_definition=SectionNoTranslation(),
            original_context=original_context,
            translated_context=translated_context,
            current_validation=current_validation,
            previous_validation=None,
        )
    )

    assert isinstance(result, Success)

    state = result.unwrap()
    assert state.context is not translated_context
    assert state.context is original_context
