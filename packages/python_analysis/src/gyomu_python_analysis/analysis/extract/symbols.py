import ast
from dataclasses import dataclass

from griffe import Alias, Attribute, Class, Function, Module, TypeAlias
from gyomu_infra.logger import logger
from gyomu_schema.option.analysis import AnalysisOption
from gyomu_schema.schemas.python.import_analysis import ImportAnalysis
from gyomu_schema.schemas.python.symbol import SymbolAnalysis
from gyomu_schema.schemas.python.types import (
    PythonPath,
)

from gyomu_python_analysis.analysis.analyzers.ast.symbol import (
    AstClassFunctionKey,
    AstTargetSymbolType,
    get_ast_index,
)
from gyomu_python_analysis.analysis.analyzers.cls import analyze_class
from gyomu_python_analysis.analysis.analyzers.context import (
    DependencyInformation,
    initialize_symbol_context,
)
from gyomu_python_analysis.analysis.analyzers.dependency import (
    resolve_dependencies,
)
from gyomu_python_analysis.analysis.analyzers.functions import analyze_function
from gyomu_python_analysis.analysis.analyzers.imports import analyze_import
from gyomu_python_analysis.analysis.analyzers.type_alias import analyze_type_alias
from gyomu_python_analysis.analysis.analyzers.variables import analyze_variable
from gyomu_python_analysis.analysis.file.source_file_context import SourceFileContext


@dataclass
class SymbolExtractContext:
    """Holds extracted symbol and import analysis context."""

    imported: tuple[ImportAnalysis, ...]
    """Import analysis results."""

    symbols: tuple[SymbolAnalysis, ...]
    """Extracted symbol analysis results."""


def extract_symbols(
    source_file: SourceFileContext,
    source_lines: list[str],
    source: str,
    option: AnalysisOption | None = None,
) -> SymbolExtractContext:
    """Extracts symbols and imports from a source file.

    Args:
        source_file (SourceFileContext): Source file context being analyzed.
        source_lines (list[str]): Lines of source code.
        source (str): Source code string.
        option (AnalysisOption | None): Optional analysis configuration options.

    Returns:
        SymbolExtractContext: Extracted symbol and import context.
    """
    imported: list[ImportAnalysis] = _extract_imports(source_file.module, source_lines)
    symbols: list[SymbolAnalysis] = _extract_symbols_internal(
        source_file, source, source_lines, imported, option
    )
    # for symbol_name, value in module.members.items():
    #     if isinstance(value, Alias):
    return SymbolExtractContext(imported=tuple(imported), symbols=tuple(symbols))


def _extract_imports(
    module: Module,
    source_lines: list[str],
) -> list[ImportAnalysis]:
    """Extracts import statements from a module.

    Args:
        module (Module): Module to extract imports from.
        source_lines (list[str]): Lines of source code.

    Returns:
        list[ImportAnalysis]: List of extracted import analyses.
    """
    imported: list[ImportAnalysis] = []
    for symbol_name, value in module.members.items():
        if isinstance(value, Alias):
            imported.append(analyze_import(value, symbol_name, source_lines))
    return imported


def _extract_symbols_internal(
    source_file: SourceFileContext,
    source: str,
    source_lines: list[str],
    imported: list[ImportAnalysis],
    option: AnalysisOption | None = None,
) -> list[SymbolAnalysis]:
    """Internal helper to extract and analyze symbols from a source file module.

    Args:
        source_file (SourceFileContext): Source file context being analyzed.
        source (str): Source code string.
        source_lines (list[str]): Lines of source code.
        imported (list[ImportAnalysis]): Extracted import analyses.
        option (AnalysisOption | None): Optional analysis configuration options.

    Returns:
        list[SymbolAnalysis]: List of extracted symbol analyses with resolved
            dependencies.

    Raises:
        ValueError: Raised when a symbol identity cannot be found in the extracted
            symbols map.
    """
    symbols: list[SymbolAnalysis] = []
    dependencies: list[DependencyInformation] = []
    module_name: PythonPath = PythonPath(source_file.module.path)
    index: (
        dict[
            AstClassFunctionKey,
            AstTargetSymbolType,
        ]
        | None
    ) = None

    logger.info(f"module_name:{module_name}")
    for symbol_name, symbol in source_file.module.members.items():
        if isinstance(symbol, Alias):
            continue
        # pprint(f"Extracting symbol: {symbol_name} ({type(symbol)})")
        # pprint(symbol.as_dict())
        context = initialize_symbol_context(
            module_name=module_name, name=symbol_name, source_lines=source_lines
        )
        if isinstance(symbol, Attribute):
            index = get_ast_index(index, source, source_path=module_name)
            assert symbol.endlineno
            ast_symbol = index.get(AstClassFunctionKey(symbol.name, symbol.endlineno))
            # print(symbol.name)
            # print(index)
            if ast_symbol is not None:
                assert isinstance(ast_symbol, ast.Assign | ast.AnnAssign)
            symbols.append(
                analyze_variable(
                    variable=symbol,
                    name=symbol_name,
                    context=context,
                    option=option,
                    asy_symbol=ast_symbol,
                )
            )
        elif isinstance(symbol, Function):
            index = get_ast_index(index, source, source_path=module_name)
            assert symbol.endlineno
            ast_symbol = index.get(AstClassFunctionKey(symbol.name, symbol.endlineno))
            assert isinstance(ast_symbol, ast.FunctionDef | ast.AsyncFunctionDef)
            symbols.append(
                analyze_function(
                    func=symbol,
                    name=symbol_name,
                    context=context,
                    option=option,
                    ast=ast_symbol,
                )
            )
        elif isinstance(symbol, Class):
            index = get_ast_index(index, source, source_path=module_name)
            assert symbol.endlineno
            ast_symbol = index.get(AstClassFunctionKey(symbol.name, symbol.endlineno))
            assert isinstance(ast_symbol, ast.ClassDef)
            symbols.append(
                analyze_class(
                    cls=symbol,
                    name=symbol_name,
                    context=context,
                    ast=ast_symbol,
                    option=option,
                )
            )

        elif isinstance(symbol, TypeAlias):
            symbols.append(
                analyze_type_alias(
                    alias=symbol, name=symbol_name, context=context, option=option
                )
            )
        for item in context.dependencies:
            dependencies.append(item)

    dependency_map = resolve_dependencies(dependencies, imported, symbols)

    symbols_by_identity = {symbol.identity: symbol for symbol in symbols}
    for identity, dependency_list in dependency_map.items():
        source_symbol = symbols_by_identity.get(identity)
        if source_symbol is None:
            raise ValueError(f"Unexpected Error. Should not happen. {repr(identity)}")
        source_symbol.dependencies = dependency_list

    return symbols
