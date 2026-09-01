from griffe import Alias
from gyomu_schema.schemas.python.import_analysis import ImportAnalysis


def analyze_import(alias: Alias, name: str) -> ImportAnalysis:
    target_path = alias.target_path
    print(f"path: {alias.path}")
    print(f"target-path: {alias.target_path}")
    # print(f"canonical_path: {alias.canonical_path}")
    return ImportAnalysis(imported_name=target_path, local_name=name)
