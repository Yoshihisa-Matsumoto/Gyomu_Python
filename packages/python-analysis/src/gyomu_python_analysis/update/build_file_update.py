from gyomu_schema.error.validation import ValidationError
from gyomu_schema.schemas.python.file_analysis import FileAnalysisContext
from gyomu_schema.schemas.python.symbol import MemberAnalysis, SymbolAnalysis
from gyomu_schema.schemas.python.symbol_base import DeclarationKind

from gyomu_python_analysis.update.docstring.file_update_plan import (
    FileUpdatePlan,
    FileUpdatePlanEntry,
)
from gyomu_python_analysis.update.docstring.rendered_symbol import (
    RenderedSymbolDocstring,
)


def build_file_update_plan(
    context: FileAnalysisContext,
    rendered_docstrings: tuple[RenderedSymbolDocstring, ...],
    source: str,
) -> FileUpdatePlan:
    entries = tuple(
        build_file_update_plan_entry(
            source=source,
            context=context,
            rendered=rendered,
        )
        for rendered in rendered_docstrings
    )

    # validate_file_update_plan_entries(entries)

    return FileUpdatePlan(items=entries)


def validate_file_update_plan_entries(
    entries: tuple[FileUpdatePlanEntry, ...],
) -> None:
    sorted_entries = sorted(
        entries,
        key=lambda entry: entry.location.start_offset,
    )

    for entry in sorted_entries:
        location = entry.location

        if location.start_offset > location.end_offset:
            raise ValidationError(
                f"Invalid file update range for "
                f"{entry.identity}: "
                f"start_offset ({location.start_offset}) is greater than "
                f"end_offset ({location.end_offset})."
            )

    for previous, current in zip(sorted_entries, sorted_entries[1:], strict=False):
        previous_end = previous.location.end_offset
        current_start = current.location.start_offset

        if current_start < previous_end:
            raise ValidationError(
                f"Overlapping file update ranges: "
                f"{previous.identity} "
                f"[{previous.location.start_offset}, {previous_end}) and "
                f"{current.identity} "
                f"[{current_start}, {current.location.end_offset})."
            )


def build_file_update_plan_entry(
    source: str,
    context: FileAnalysisContext,
    rendered: RenderedSymbolDocstring,
) -> FileUpdatePlanEntry:
    analysis = context.metadata.symbols.get(rendered.identity)

    if analysis is None:
        raise ValidationError(
            message=f"Declaration Item Not Found for {repr(rendered.identity)}"
        )

    if analysis.location is None or analysis.indent is None:
        raise ValidationError(
            message=f"Declation Item is constructor parameter :{repr(rendered.identity)} "
        )

    if rendered.location.start_offset == rendered.location.end_offset:
        return build_addition_entry(
            analysis=analysis,
            rendered=rendered,
        )

    if rendered.docstring == "" or rendered.docstring is None:
        return build_deletion_entry(
            source=source,
            rendered=rendered,
        )

    return build_replacement_entry(rendered)


def build_addition_entry(
    analysis: SymbolAnalysis | MemberAnalysis,
    rendered: RenderedSymbolDocstring,
) -> FileUpdatePlanEntry:
    assert analysis.indent
    new_indent = analysis.indent
    if analysis.kind == DeclarationKind.CLASS:
        new_indent += 4
    assert rendered.docstring
    assert analysis.location
    location = analysis.location
    new_location = location.model_copy()
    new_location.start_offset = location.start_offset + new_indent
    return FileUpdatePlanEntry(
        identity=rendered.identity, location=new_location, new_text=rendered.docstring
    )


def build_deletion_entry(
    source: str, rendered: RenderedSymbolDocstring
) -> FileUpdatePlanEntry:
    location = rendered.location.model_copy()

    start = location.start_offset
    while start > 0 and source[start - 1] in " \t":
        start -= 1

    end = location.end_offset
    while end < len(source) and source[end] in " \t":
        end += 1

    location.start_offset = start
    location.end_offset = end

    return FileUpdatePlanEntry(
        identity=rendered.identity,
        location=location,
        new_text="",
    )


def build_replacement_entry(rendered: RenderedSymbolDocstring) -> FileUpdatePlanEntry:
    assert rendered.docstring
    return FileUpdatePlanEntry(
        identity=rendered.identity,
        location=rendered.location,
        new_text=rendered.docstring,
    )
