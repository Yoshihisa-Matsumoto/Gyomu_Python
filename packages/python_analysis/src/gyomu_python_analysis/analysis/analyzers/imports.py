import ast

from griffe import Alias
from gyomu_schema.schemas.python.import_analysis import ImportAnalysis, ImportKind


def analyze_import(
    alias: Alias,
    name: str,
    source_lines: list[str],
) -> ImportAnalysis | None:
    """Analyzes an import statement and returns its details.

    Args:
        alias (Alias): Import alias information
        name (str): Local name of the imported symbol
        source_lines (list[str]): Source code lines

    Returns:
        ImportAnalysis: Resulting import analysis details
    """
    target_path = alias.target_path
    attr = alias.as_dict()
    # print(attr)
    # print(f"path: {alias.path}")
    # print(f"target-path: {alias.target_path}")
    # print(f"canonical_path: {alias.canonical_path}")
    assert attr["lineno"]
    target_line = source_lines[int(attr["lineno"]) - 1]
    kind = ImportKind.MODULE
    if target_line.strip().startswith("from"):
        kind = ImportKind.SYMBOL
    if kind == ImportKind.MODULE:
        return None
    return ImportAnalysis(imported_name=target_path, local_name=name, kind=kind)


def analyze_ast_import(ast: ast.Import) -> list[ImportAnalysis]:
    analysis_list: list[ImportAnalysis] = []
    for name_attr in ast.names:
        imported_name = name_attr.name
        local_name = (
            name_attr.asname
            if name_attr.asname is not None
            else imported_name.split(".", maxsplit=1)[0]
        )
        analysis_list.append(
            ImportAnalysis(
                imported_name=imported_name,
                local_name=local_name,
                kind=ImportKind.MODULE,
            )
        )

    return analysis_list
