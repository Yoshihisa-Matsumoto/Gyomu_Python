from gyomu_schema.schemas.document.content import (
    DocumentContentType,
    Paragraph,
)
from gyomu_schema.schemas.document.definition.common import validate_text
from gyomu_schema.schemas.document.section import (
    DocumentContentDefinitionBase,
    ReconciliationValidator,
)
from gyomu_schema.schemas.document.validation import ValidationIssue, ValidationResult


def _validate_paragraph(source: Paragraph, destination: Paragraph) -> ValidationResult:
    """Validates source and destination paragraphs.

    Validates paragraph content during reconciliation.

    Args:
        source (Paragraph): Source paragraph content
        destination (Paragraph): Destination paragraph content

    Returns:
        ValidationResult: Validation result indicating whether the paragraph content is
            valid
    """
    issues: list[ValidationIssue] = []
    validate_text(
        source=source.text, destination=destination.text, location="text", issues=issues
    )
    return ValidationResult(issues=tuple(issues), is_valid=len(issues) == 0)


paragraph_definition = DocumentContentDefinitionBase[Paragraph](
    kind=DocumentContentType.PARAGRAPH,
    content_schema=Paragraph,
    reconciliation=ReconciliationValidator[Paragraph](validate=_validate_paragraph),
    translation_instruction="Translate only the `text` field.",
)
"""Content definition for paragraph documents.

Defines content definition and validation rules for paragraph document content.
"""
