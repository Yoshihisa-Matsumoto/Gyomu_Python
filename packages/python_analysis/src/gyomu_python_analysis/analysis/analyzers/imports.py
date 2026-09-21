from griffe import Alias
from gyomu_schema.schemas.python.import_analysis import ImportAnalysis, ImportKind


def analyze_import(
    alias: Alias,
    name: str,
    source_lines: list[str],
) -> ImportAnalysis:
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
    return ImportAnalysis(imported_name=target_path, local_name=name, kind=kind)
