from gyomu_schema.schemas.document.content import (
    DocumentContentType,
    Paragraph,
)
from gyomu_schema.schemas.document.section import (
    DocumentContentDefinitionBase,
    ReconciliationValidator,
)
from gyomu_schema.schemas.document.validation import ValidationResult


def _validate_paragraph(source: Paragraph, destination: Paragraph) -> ValidationResult:
    return ValidationResult(issues=tuple(), is_valid=True)


paragraph_definition = DocumentContentDefinitionBase[Paragraph](
    kind=DocumentContentType.PARAGRAPH,
    content_schema=Paragraph,
    reconciliation=ReconciliationValidator[Paragraph](validate=_validate_paragraph),
    translation_instruction="Translate only the `text` field.",
)
