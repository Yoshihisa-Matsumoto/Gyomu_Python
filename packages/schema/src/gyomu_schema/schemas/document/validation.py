from pydantic import BaseModel


class ValidationIssue(BaseModel):
    code: str
    message: str
    repair_instruction: str
    translation_id: int | None = None
    details: dict[str, str] | None = None


class ValidationResult(BaseModel):
    issues: tuple[ValidationIssue, ...]

    is_valid: bool
