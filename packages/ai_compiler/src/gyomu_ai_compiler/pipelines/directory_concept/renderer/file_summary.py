from gyomu_schema.schemas.concept.file_summary import (
    FileSummary,
    PublicDeclarationSummary,
)


def render_file_summary(context: FileSummary) -> str:
    """Render a file summary string from the given FileSummary context.

    Returns:
        str: The rendered file summary string.
    """
    return (
        f"File path:\n"
        f"{context.path}\n"
        f"\n"
        f"Exported symbols:\n"
        f"{
            '\n\n'.join(
                build_export_symbol_input(summary) for summary in context.exports
            )
        }\n"
    )


def build_export_symbol_input(symbol: PublicDeclarationSummary) -> str:
    """Build a formatted string representation of a public declaration summary for
    export.

    Returns:
        str: The formatted export symbol input string.
    """
    return f"- {symbol.symbol} ({symbol.kind})\n  Summary:\n  {symbol.summary}"
