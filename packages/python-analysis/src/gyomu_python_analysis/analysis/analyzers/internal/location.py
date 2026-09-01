from griffe import Object
from gyomu_schema.schemas.python.location import SourceLocation


def calculate_symbol_location(
    symbol: Object,
    source_lines: list[str],
) -> SourceLocation:
    # source_full_path = project.project_root / project.source_root / source_file.path
    start_line_no = symbol.lineno
    end_line_no = symbol.endlineno

    assert start_line_no is not None
    assert end_line_no is not None

    # source_lines = source_full_path.read_text(
    #     encoding="utf-8",
    # ).splitlines()

    start_line = source_lines[start_line_no - 1]
    end_line = source_lines[end_line_no - 1]

    start_column = len(start_line) - len(start_line.lstrip())
    end_column = len(end_line.rstrip())

    return SourceLocation(
        start_line=start_line_no,
        start_column=start_column,
        end_line=end_line_no,
        end_column=end_column,
    )


def calculate_member_location(
    symbol: Object,
    source_lines: list[str],
    parent_location: SourceLocation | None,
) -> SourceLocation | None:
    location = calculate_symbol_location(symbol=symbol, source_lines=source_lines)
    if parent_location is not None and (
        location.start_line >= parent_location.start_line
        and location.end_line <= parent_location.end_line
    ):
        return None
    return location
