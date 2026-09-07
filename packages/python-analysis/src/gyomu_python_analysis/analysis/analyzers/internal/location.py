from griffe import Decorator, Docstring, Object
from gyomu_schema.schemas.python.location import SourceLocation

from gyomu_python_analysis.analysis.analyzers.context import SymbolContext


def _calculate_location(
    target: Object | Docstring | Decorator, context: SymbolContext
) -> SourceLocation:
    # source_full_path = project.project_root / project.source_root / source_file.path
    start_line_no = target.lineno
    end_line_no = target.endlineno

    assert start_line_no is not None
    assert end_line_no is not None

    start_line = context.source_lines[start_line_no - 1]
    end_line = context.source_lines[end_line_no - 1]

    start_column = len(start_line) - len(start_line.lstrip())
    end_column = len(end_line.rstrip())

    start_offset = context.line_start_offsets[start_line_no - 1] + start_column
    end_offset = context.line_start_offsets[end_line_no - 1] + end_column

    return SourceLocation(
        start_line=start_line_no,
        start_column=start_column,
        end_line=end_line_no,
        end_column=end_column,
        start_offset=start_offset,
        end_offset=end_offset,
    )


def calculate_symbol_location(
    symbol: Object,
    context: SymbolContext,
) -> SourceLocation:
    return _calculate_location(symbol, context)


def calculate_member_location(
    symbol: Object,
    context: SymbolContext,
    parent_location: SourceLocation | None,
) -> SourceLocation | None:
    location = calculate_symbol_location(symbol=symbol, context=context)
    if parent_location is not None and (
        location.start_line >= parent_location.start_line
        and location.end_line <= parent_location.end_line
    ):
        return None
    return location


def calculate_docstring_location(
    doc: Docstring,
    context: SymbolContext,
) -> SourceLocation:
    return _calculate_location(target=doc, context=context)


def calculate_decorator_location(
    decorator: Decorator,
    context: SymbolContext,
) -> SourceLocation:
    return _calculate_location(target=decorator, context=context)
