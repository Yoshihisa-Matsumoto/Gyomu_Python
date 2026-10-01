from gyomu_schema.schemas.document.content import CodeBlock, DocumentContentType
from gyomu_schema.schemas.document.section import (
    DocumentContentDefinitionBase,
    ReconciliationValidator,
)
from gyomu_schema.schemas.document.validation import ValidationIssue, ValidationResult


def _validate_codeblock(source: CodeBlock, destination: CodeBlock) -> ValidationResult:
    issues: list[ValidationIssue] = []
    if source.title and not destination.title:
        issues.append(
            ValidationIssue(
                code="CODE_BLOCK_TITLE_MISMATCH",
                message="Title is not translated",
                repair_instruction="Translate code block title properly",
            )
        )
    elif not source.title and destination.title:
        issues.append(
            ValidationIssue(
                code="CODE_BLOCK_TITLE_MISMATCH",
                message="Title is created from nothing",
                repair_instruction="Must not create sentense from non-existence title",
            )
        )
    if source.code != destination.code:
        issues.append(
            ValidationIssue(
                code="CODE_BLOCK_CODE_MISMATCH",
                message="code is translated",
                repair_instruction="code MUST not be translated or transformed",
            )
        )
    if source.language != destination.language:
        issues.append(
            ValidationIssue(
                code="CODE_BLOCK_LANGUAGE_MISMATCH",
                message="language is translated",
                repair_instruction="language MUST not be translated or transformed",
            )
        )
    return ValidationResult(issues=tuple(issues), is_valid=len(issues) == 0)


code_block_definition = DocumentContentDefinitionBase[CodeBlock](
    kind=DocumentContentType.CODE,
    content_schema=CodeBlock,
    reconciliation=ReconciliationValidator[CodeBlock](validate=_validate_codeblock),
    translation_instruction=(
        "Translate only the `title` field if it exists. "
        "If the `title` field does not exist, do not create one."
    ),
)
