from gyomu_schema.schemas.python.module import ModuleAnalysis
from gyomu_schema.schemas.python.symbol import SymbolAnalysis

# def find_import_by_local_name(
#     local_name: str, module: ModuleAnalysis
# ) -> ImportAnalysis | None:
#     target_import = next(
#         (imp for imp in module.imports if imp.local_name == local_name), None
#     )
#     return target_import


def find_symbol_by_name(name: str, module: ModuleAnalysis) -> SymbolAnalysis | None:
    target_symbol = next((sym for sym in module.symbols if sym.name == name), None)
    return target_symbol
