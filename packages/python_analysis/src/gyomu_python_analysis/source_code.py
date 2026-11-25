from gyomu_schema.schemas.python.file_analysis import FileAnalysisContext


def get_import_insertion_line(helper_file_analysis: FileAnalysisContext) -> int:
    min_start_line: int = 9999
    for symbol in helper_file_analysis.analysis.symbols:
        start_line = symbol.location.start_line
        if min_start_line > start_line:
            min_start_line = start_line

    max_import_line: int = 0
    for import_symbol in helper_file_analysis.analysis.imports:
        if (
            import_symbol.end_line < min_start_line
            and import_symbol.end_line > max_import_line
        ):
            max_import_line = import_symbol.end_line
    return max_import_line
