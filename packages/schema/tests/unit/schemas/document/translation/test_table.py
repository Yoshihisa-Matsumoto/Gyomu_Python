from gyomu_schema.schemas.document.content import Table
from gyomu_schema.schemas.document.section import RetryContextArg, SectionNoTranslation
from gyomu_schema.schemas.document.translation.table import (
    _update_table_retry_context,
)
from returns.result import Success

from packages.schema.schema_test_support.concept_helpers import (
    create_table,
    create_table_row,
    create_validation_result,
)


def test_update_retry_context_returns_original_context_and_validation() -> None:
    original_context = create_table(
        header=create_table_row(
            cells=("Name", "Description"),
        ),
        rows=(
            create_table_row(
                cells=("Alice", "Engineer"),
            ),
        ),
    )
    current_validation = create_validation_result()

    result = _update_table_retry_context(
        RetryContextArg[Table](
            section_id="section-1",
            section_definition=SectionNoTranslation(),
            original_context=original_context,
            translated_context=create_table(
                header=create_table_row(cells=("名前",)),
                rows=(
                    create_table_row(
                        cells=("Alice", "Engineer"),
                    ),
                ),
            ),
            current_validation=current_validation,
            previous_validation=None,
        )
    )

    assert isinstance(result, Success)

    state = result.unwrap()
    assert state.context is original_context
    assert state.validation is current_validation


def test_update_retry_context_does_not_use_translated_context() -> None:
    original_context = create_table(
        header=create_table_row(
            cells=("Name", "Description"),
        ),
        rows=(
            create_table_row(
                cells=("Alice", "Engineer"),
            ),
        ),
    )
    translated_context = create_table(
        header=create_table_row(cells=("名前",)),
        rows=(
            create_table_row(
                cells=("Alice", "Engineer"),
            ),
        ),
    )
    current_validation = create_validation_result()

    result = _update_table_retry_context(
        RetryContextArg[Table](
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
