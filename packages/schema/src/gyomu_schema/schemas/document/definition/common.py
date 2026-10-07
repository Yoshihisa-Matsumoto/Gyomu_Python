from gyomu_schema.schemas.document.validation import ValidationIssue


def validate_text(
    source: str, destination: str, location: str, issues: list[ValidationIssue]
) -> None:
    source_count = source.count("\\n")
    destination_count = destination.count("\\n")

    if source_count != destination_count:
        issue = ValidationIssue(
            code="LITERAL_NEWLINE_MISMATCH",
            message=(
                f"The number of literal '\\n' sequences is different in {location}."
            ),
            details={
                "source_count": str(source_count),
                "translated_count": str(destination_count),
            },
            repair_instruction=(
                "- Preserve the same number of literal `\\n` sequences "
                "as in the source.\n"
                "- Do not add, remove, or replace literal `\\n` sequences."
            ),
        )
        issues.append(issue)
