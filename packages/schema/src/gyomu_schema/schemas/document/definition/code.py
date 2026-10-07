from gyomu_schema.schemas.document.content import CodeBlock, DocumentContentType
from gyomu_schema.schemas.document.section import (
    DocumentContentDefinitionBase,
    ReconciliationValidator,
)
from gyomu_schema.schemas.document.validation import ValidationIssue, ValidationResult


def _validate_codeblock(source: CodeBlock, destination: CodeBlock) -> ValidationResult:
    """Validates source and destination CodeBlock instances for reconciliation.

    Returns:
        ValidationResult: Validation result containing any issues found during code
            block comparison.

    Args:
        source (CodeBlock): Source code block instance to compare.
        destination (CodeBlock): Destination code block instance to validate.
    """
    issues: list[ValidationIssue] = []
    if source.title and not destination.title:
        issues.append(
            ValidationIssue(
                code="CODE_BLOCK_TITLE_MISMATCH",
                message=("Code block title is missing from the translation."),
                repair_instruction=(
                    "Translate the code block title when the source has one."
                ),
            )
        )
    elif not source.title and destination.title:
        issues.append(
            ValidationIssue(
                code="CODE_BLOCK_TITLE_MISMATCH",
                message=(
                    "Code block title was created although the source has no title."
                ),
                repair_instruction=(
                    "Must not create a title from when the source has no title."
                ),
            )
        )

    if destination.title:
        destination_count = destination.title.count("\n")
        if destination_count > 0:
            issue = ValidationIssue(
                code="CODE_BLOCK_TITLE_MULTILINE",
                message="Code block title must be a single line.",
                details={
                    "line_break_count": str(destination_count),
                },
                repair_instruction=(
                    "- Keep the code block title on a single line.\n"
                    "- Remove all line breaks from the code block title."
                ),
            )
            issues.append(issue)

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
"""Content definition for CodeBlock elements, specifying validation and translation
instructions.
"""
