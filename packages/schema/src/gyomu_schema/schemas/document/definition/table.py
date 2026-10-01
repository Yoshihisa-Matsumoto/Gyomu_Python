from gyomu_schema.schemas.document.content import DocumentContentType, Table
from gyomu_schema.schemas.document.section import (
    DocumentContentDefinitionBase,
    ReconciliationValidator,
)
from gyomu_schema.schemas.document.validation import ValidationIssue, ValidationResult


def _validate_table(source: Table, destination: Table) -> ValidationResult:
    issues: list[ValidationIssue] = []
    if len(source.header.cells) != len(destination.header.cells):
        issues.append(
            ValidationIssue(
                code="TABLE_HEADER_CELL_COUNT_CHANGED",
                message=(
                    "The translated table contains a different number "
                    "of cells on header."
                ),
                details={
                    "source_count": str(len(source.header.cells)),
                    "translated_count": str(len(destination.header.cells)),
                },
                repair_instruction=(
                    "Translate again while preserving every "
                    "table cells on header & rows"
                ),
            )
        )
    if len(issues) == 0:
        column_count = len(source.header.cells)
        if len(source.rows) != len(destination.rows):
            issues.append(
                ValidationIssue(
                    code="TABLE_ROWS_COUNT_CHANGED",
                    message=(
                        "The translated table contains a different number of rows."
                    ),
                    details={
                        "source_count": str(len(source.rows)),
                        "translated_count": str(len(destination.rows)),
                    },
                    repair_instruction=(
                        "Translate again while preserving every table rows"
                    ),
                )
            )

        if len(issues) == 0:
            for index, source_row in enumerate(source.rows):
                destination_row = destination.rows[index]
                if (
                    len(source_row.cells) != len(destination_row.cells)
                    or len(source_row.cells) != column_count
                ):
                    issues.append(
                        ValidationIssue(
                            code="TABLE_ROW_CELL_COUNT_CHANGED",
                            message=(
                                "The translated table row contains a "
                                "different number of cells ."
                            ),
                            translation_id=index,
                            details={
                                "source_count": str(len(source_row.cells)),
                                "translated_count": str(len(destination_row.cells)),
                            },
                            repair_instruction=(
                                "Translate again while preserving "
                                "every table cells on  rows"
                            ),
                        )
                    )

    return ValidationResult(issues=tuple(issues), is_valid=len(issues) == 0)


table_definition = DocumentContentDefinitionBase[Table](
    kind=DocumentContentType.TABLE,
    content_schema=Table,
    reconciliation=ReconciliationValidator[Table](validate=_validate_table),
    translation_instruction=(
        "Translate only the text content in `header.cells` and `rows[*].cells`. "
        "Preserve the table structure, including the number of columns and rows."
    ),
)
