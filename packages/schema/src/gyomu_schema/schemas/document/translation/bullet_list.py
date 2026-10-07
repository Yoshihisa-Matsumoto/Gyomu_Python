from returns.result import Failure, Result, Success

from gyomu_schema.error.translation import TranslationError
from gyomu_schema.schemas.document.content import BulletList, BulletListItem
from gyomu_schema.schemas.document.definition.bullent_list import bullet_list_definition
from gyomu_schema.schemas.document.section import (
    DocumentContentTranslationStrategy,
    RetryContextArg,
    TranslationState,
)
from gyomu_schema.schemas.document.validation import ValidationResult


def _find_bullet_list_item_from_item(
    item: BulletListItem, translation_id: int
) -> BulletListItem | None:
    """Find a bullet list item matching the specified translation ID."""

    if item.translation_id == translation_id:
        return item
    if item.children is not None:
        for child in item.children:
            found_item = _find_bullet_list_item_from_item(child, translation_id)
            if found_item is not None:
                return found_item

    return None


def _find_bullet_list_item(
    bullet_list: BulletList,
    translation_id: int,
) -> BulletListItem | None:
    """Find a bullet list item in a bullet list by translation ID."""

    for item in bullet_list.items:
        found_item = _find_bullet_list_item_from_item(item, translation_id)
        if found_item is not None:
            return found_item

    return None


def _update_bullet_list_retry_context(
    args: RetryContextArg[BulletList],
) -> Result[TranslationState[BulletList], TranslationError]:
    """Update bullet list retry context during translation."""

    current_validation = args.current_validation
    previous_validation = args.previous_validation
    original_context = args.original_context
    translated_context = args.translated_context

    active_validation_list = _merge_validation_result(
        current_validation, previous_validation, original_context
    )

    valid_id_list = _retrieve_valid_id_list(active_validation_list, original_context)
    previous_valid_id_list = (
        _retrieve_valid_id_list(previous_validation, original_context)
        if previous_validation is not None
        else tuple()
    )

    for translation_id in valid_id_list:
        if translation_id in previous_valid_id_list:
            continue
        valid_item = _find_bullet_list_item(original_context, translation_id)
        valid_item_from_result = _find_bullet_list_item(
            translated_context, translation_id
        )

        if valid_item is None or valid_item_from_result is None:
            return Failure(
                TranslationError(
                    content_type="bullet-list",
                    message="TranslationId Not Found on BulletList",
                    phase="retry-context",
                    section_id=args.section_id,
                    translation_id=translation_id,
                )
            )
        valid_item.text = valid_item_from_result.text

    return Success(
        TranslationState(context=original_context, validation=active_validation_list)
    )


def _retrieve_valid_id_list(
    validation: ValidationResult, context: BulletList
) -> tuple[int, ...]:
    """Retrieve a tuple of valid translation IDs from a bullet list and validation
    result.
    """
    invalid_id_list = [
        issue.translation_id
        for issue in validation.issues
        if issue.translation_id is not None
    ]
    valid_id_list: list[int] = []

    for item in context.items:
        result = _retrieve_valid_id_list_item(invalid_id_list, item)
        valid_id_list.extend(result)

    return tuple(valid_id_list)


def _retrieve_valid_id_list_item(
    invalid_id_list: list[int], item: BulletListItem
) -> list[int]:
    """Retrieve valid translation IDs from a bullet list item recursively."""

    valid_id_list: list[int] = []

    if item.translation_id not in invalid_id_list:
        valid_id_list.append(item.translation_id)

    if item.children is not None:
        for child in item.children:
            result = _retrieve_valid_id_list_item(invalid_id_list, child)
            valid_id_list.extend(result)

    return valid_id_list


def _merge_validation_result(
    current_validation: ValidationResult,
    previous_validation: ValidationResult | None,
    context: BulletList,
) -> ValidationResult:
    """Merge current and previous validation results for a bullet list."""

    if not previous_validation:
        return current_validation
    if any(issue.translation_id is None for issue in previous_validation.issues):
        return current_validation

    valid_id_list = _retrieve_valid_id_list(previous_validation, context)

    filtered_issues = [
        issue
        for issue in current_validation.issues
        if issue.translation_id is not None and issue.translation_id in valid_id_list
    ]

    return ValidationResult(
        issues=tuple(filtered_issues), is_valid=len(filtered_issues) == 0
    )


bullet_list_translation_strategy = DocumentContentTranslationStrategy[BulletList](
    definition=bullet_list_definition,
    retry_context_updater=_update_bullet_list_retry_context,
)
"""Translation strategy definition for bullet list content."""
