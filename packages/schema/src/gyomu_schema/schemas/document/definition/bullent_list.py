from gyomu_schema.schemas.document.content import (
    BulletList,
    BulletListItem,
    DocumentContentType,
)
from gyomu_schema.schemas.document.section import (
    DocumentContentDefinitionBase,
    ReconciliationValidator,
)
from gyomu_schema.schemas.document.validation import ValidationIssue, ValidationResult


def _validate_bullet_list_item(
    source: BulletListItem,
    destination: BulletListItem,
    translation_id: int,
    issues: list[ValidationIssue],
) -> None:
    """Validate bullet list item translation consistency."""

    source_item_count = 0 if source.children is None else len(source.children)
    destination_item_count = (
        0 if destination.children is None else len(destination.children)
    )
    if source_item_count != destination_item_count:
        issues.append(
            ValidationIssue(
                code="BULLET_LIST_ITEM_COUNT_CHANGED",
                message=(
                    "The translated bullet list contains a different number of items."
                ),
                translation_id=translation_id,
                details={
                    "source_count": str(source_item_count),
                    "translated_count": str(destination_item_count),
                },
                repair_instruction=(
                    "Translate again while preserving every bullet item "
                    f"from the source for translation_id={source.translation_id}."
                ),
            )
        )
    elif source.children is not None and destination.children is not None:
        is_valid = True
        for index, source_child in enumerate(source.children):
            if is_valid:
                destination_child = destination.children[index]
                if source_child.translation_id != destination_child.translation_id:
                    is_valid = False
                    issues.append(
                        ValidationIssue(
                            code="BULLET_LIST_ITEM_TRANSLATIONID_MISMATCH",
                            message=(
                                "The translated bullet list has mismatched "
                                "translation_id"
                            ),
                            translation_id=translation_id,
                            repair_instruction=(
                                "BulletListItem's translation_id must be same"
                            ),
                        )
                    )
        if is_valid:
            for index, source_child in enumerate(source.children):
                destination_child = destination.children[index]
                _validate_bullet_list_item(
                    source_child, destination_child, source_child.translation_id, issues
                )


def _validate_bullet_list(
    source: BulletList, destination: BulletList
) -> ValidationResult:
    """Validate bullet list translation consistency."""

    issues: list[ValidationIssue] = []

    if len(source.items) != len(destination.items):
        issues.append(
            ValidationIssue(
                code="BULLET_LIST_ITEM_COUNT_CHANGED",
                message=(
                    "The translated bullet list contains a different number of items."
                ),
                details={
                    "source_count": str(len(source.items)),
                    "translated_count": str(len(destination.items)),
                },
                repair_instruction=(
                    "Translate again while preserving every bullet item "
                    "from the source."
                ),
            )
        )
    else:
        is_valid = True
        for index, source_item in enumerate(source.items):
            destination_item = destination.items[index]
            if source_item.translation_id != destination_item.translation_id:
                is_valid = False
                issues.append(
                    ValidationIssue(
                        code="BULLET_LIST_ITEM_TRANSLATIONID_MISMATCH",
                        message=(
                            "The translated bullet list has mismatched translation_id"
                        ),
                        repair_instruction=(
                            "BulletListItem's translation_id must be same"
                        ),
                    )
                )
        if is_valid:
            for index, source_item in enumerate(source.items):
                destination_item = destination.items[index]
                _validate_bullet_list_item(
                    source_item, destination_item, source_item.translation_id, issues
                )

    return ValidationResult(issues=tuple(issues), is_valid=len(issues) == 0)


bullet_list_definition = DocumentContentDefinitionBase[BulletList](
    kind=DocumentContentType.BULLET_LIST,
    content_schema=BulletList,
    reconciliation=ReconciliationValidator[BulletList](validate=_validate_bullet_list),
    translation_instruction=(
        "Translate only the `text` field of each BulletListItem. "
        "Do not translate or modify `translation_id` or the `children` structure."
    ),
)
"""Document content definition for bullet lists."""
