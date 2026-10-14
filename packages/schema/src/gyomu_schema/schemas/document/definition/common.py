from gyomu_schema.schemas.document.validation import ValidationIssue


def validate_text(
    source: str, destination: str, location: str, issues: list[ValidationIssue]
) -> None:
    """Validates literal newline counts between source and destination text.

    Args:
        source (str): Source text
        destination (str): Destination text
        location (str): Location identifier for reporting
        issues (list[ValidationIssue]): List to append validation issues to

    Returns:
        None: None
    """
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


def validate_textblock(
    source: tuple[str, ...],
    destination: tuple[str, ...],
    location: str,
    issues: list[ValidationIssue],
) -> None:
    """Validate line structure and literal newline sequences in a text block.

    Args:
        source (tuple[str, ...]): Original text lines.
        destination (tuple[str, ...]): Translated text lines.
        location (str): Location identifier for reporting.
        issues (list[ValidationIssue]): List to append validation issues to.

    Returns:
        None: None
    """
    if len(source) != len(destination):
        issues.append(
            ValidationIssue(
                code="TEXTBLOCK_LINE_COUNT_MISMATCH",
                message=f"The number of lines is different in {location}.",
                details={
                    "source_count": str(len(source)),
                    "translated_count": str(len(destination)),
                },
                repair_instruction=(
                    "- Preserve the same number of lines as in the source.\n"
                    "- Do not add, remove, split, or merge lines."
                ),
            )
        )

    for line_number, (source_line, destination_line) in enumerate(
        zip(source, destination, strict=False),
        start=1,
    ):
        line_location = f"{location}[line {line_number}]"

        if "\n" in destination_line or "\r" in destination_line:
            issues.append(
                ValidationIssue(
                    code="TEXTBLOCK_LINE_BREAK_FOUND",
                    message=(
                        f"An actual line break is present within {line_location}."
                    ),
                    details={
                        "line_number": str(line_number),
                    },
                    repair_instruction=(
                        "- Each line element must contain only one line.\n"
                        "- Remove actual newline characters from the line "
                        "and preserve the original line structure."
                    ),
                )
            )

        source_count = source_line.count("\\n")
        destination_count = destination_line.count("\\n")

        if source_count != destination_count:
            issues.append(
                ValidationIssue(
                    code="LITERAL_NEWLINE_MISMATCH",
                    message=(
                        "The number of literal '\\n' sequences is different "
                        f"in {line_location}."
                    ),
                    details={
                        "line_number": str(line_number),
                        "source_count": str(source_count),
                        "translated_count": str(destination_count),
                    },
                    repair_instruction=(
                        "- Preserve the same number of literal `\\n` "
                        "sequences as in the corresponding source line.\n"
                        "- Do not add, remove, or replace literal `\\n` "
                        "sequences."
                    ),
                )
            )
