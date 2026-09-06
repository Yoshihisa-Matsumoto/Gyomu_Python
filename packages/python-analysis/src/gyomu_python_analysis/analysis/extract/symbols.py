from dataclasses import dataclass

from griffe import Alias, Attribute, Class, Function, Module, TypeAlias
from gyomu_infra.logger import logger
from gyomu_schema.schemas.python.import_analysis import ImportAnalysis
from gyomu_schema.schemas.python.symbol import SymbolAnalysis
from gyomu_schema.schemas.python.types import PythonPath

from gyomu_python_analysis.analysis.analyzers.cls import analyze_class
from gyomu_python_analysis.analysis.analyzers.context import initialize_symbol_context
from gyomu_python_analysis.analysis.analyzers.functions import analyze_function
from gyomu_python_analysis.analysis.analyzers.imports import analyze_import
from gyomu_python_analysis.analysis.analyzers.type_alias import analyze_type_alias
from gyomu_python_analysis.analysis.analyzers.variables import analyze_variable
from gyomu_python_analysis.analysis.file.source_file_context import SourceFileContext


@dataclass
class SymbolExtractContext:
    imported: tuple[ImportAnalysis, ...]
    symbols: tuple[SymbolAnalysis, ...]


def extract_symbols(
    source_file: SourceFileContext,
    source_lines: list[str],
) -> SymbolExtractContext:
    imported: list[ImportAnalysis] = _extract_imports(source_file.module)
    symbols: list[SymbolAnalysis] = _extract_symbols_internal(
        source_file, source_lines, tuple(imported)
    )
    # for symbol_name, value in module.members.items():
    #     if isinstance(value, Alias):
    return SymbolExtractContext(imported=tuple(imported), symbols=tuple(symbols))


def _extract_imports(module: Module) -> list[ImportAnalysis]:
    imported: list[ImportAnalysis] = []
    for symbol_name, value in module.members.items():
        if isinstance(value, Alias):
            imported.append(analyze_import(value, symbol_name))
    return imported


def _extract_symbols_internal(
    source_file: SourceFileContext,
    source_lines: list[str],
    imports: tuple[ImportAnalysis, ...],
) -> list[SymbolAnalysis]:
    symbols: list[SymbolAnalysis] = []
    module_name: PythonPath = PythonPath(source_file.module.path)
    logger.info(f"module_name:{module_name}")
    for symbol_name, symbol in source_file.module.members.items():
        if isinstance(symbol, Alias):
            continue
        # pprint(f"Extracting symbol: {symbol_name} ({type(symbol)})")
        # pprint(symbol.as_dict())
        if isinstance(symbol, Attribute):
            symbols.append(
                analyze_variable(
                    variable=symbol,
                    name=symbol_name,
                    source_lines=source_lines,
                    context=initialize_symbol_context(
                        imports=imports,
                        module_name=module_name,
                        name=symbol_name,
                    ),
                )
            )
        elif isinstance(symbol, Function):
            symbols.append(
                analyze_function(
                    func=symbol,
                    name=symbol_name,
                    source_lines=source_lines,
                    context=initialize_symbol_context(
                        imports=imports,
                        module_name=module_name,
                        name=symbol_name,
                    ),
                )
            )
        elif isinstance(symbol, Class):
            symbols.append(
                analyze_class(
                    cls=symbol,
                    name=symbol_name,
                    source_lines=source_lines,
                    context=initialize_symbol_context(
                        imports=imports,
                        module_name=module_name,
                        name=symbol_name,
                    ),
                )
            )

        elif isinstance(symbol, TypeAlias):
            symbols.append(
                analyze_type_alias(
                    alias=symbol,
                    name=symbol_name,
                    source_lines=source_lines,
                    context=initialize_symbol_context(
                        imports=imports, module_name=module_name, name=symbol_name
                    ),
                )
            )
    return symbols
