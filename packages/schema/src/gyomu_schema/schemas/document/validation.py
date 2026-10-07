from pydantic import BaseModel


class ValidationIssue(BaseModel):
    """Defines a validation issue with a code, message, and repair instructions.

    Represents a validation issue with an error code, message, repair instructions, and
    optional context.
    """

    code: str
    """The error code representing the validation issue.

    The error code representing the validation issue.
    """
    message: str
    """The descriptive error message for the validation issue.

    The descriptive error message for the validation issue.
    """
    repair_instruction: str
    """Instructions on how to repair or resolve the validation issue.

    Instructions on how to repair or resolve the validation issue.
    """
    translation_id: int | None = None
    """Optional translation identifier associated with the issue.

    Optional translation identifier associated with the issue.
    """
    details: dict[str, str] | None = None
    """Additional contextual details regarding the validation issue.

    Additional contextual details regarding the validation issue.
    """


class ValidationResult(BaseModel):
    """Defines the overall result of a validation check including any identified issues.

    Represents the outcome of a document validation check, containing a collection of
    validation issues and an overall validity flag.
    """

    issues: tuple[ValidationIssue, ...]
    """Collection of validation issues identified during the check.

    Collection of validation issues identified during the check.
    """

    is_valid: bool
    """Flag indicating whether the document is valid overall.

    Flag indicating whether the document is valid overall.
    """
