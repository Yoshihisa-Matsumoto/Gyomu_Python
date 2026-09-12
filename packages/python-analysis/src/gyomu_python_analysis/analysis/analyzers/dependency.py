from gyomu_schema.schemas.python.dependency import (
    DependencyAnalysis,
    ImportedSymbolDependency,
    LocalFileDependency,
)
from gyomu_schema.schemas.python.import_analysis import ImportAnalysis, ImportKind
from gyomu_schema.schemas.python.symbol import SymbolAnalysis
from gyomu_schema.schemas.python.types import DeclarationIdentity, SymbolId

from gyomu_python_analysis.analysis.analyzers.context import (
    DependencyInformation,
    SymbolContext,
)

PYTHON_RESERVED_TYPE_NAMES: frozenset[str] = frozenset(
    {
        # Built-in scalar types
        "bool",
        "int",
        "float",
        "complex",
        "str",
        "bytes",
        "bytearray",
        "memoryview",
        # Built-in container types
        "list",
        "tuple",
        "dict",
        "set",
        "frozenset",
        # Built-in utility types
        "range",
        "object",
        "type",
        # Typing primitives
        "Any",
        "Never",
        "NoReturn",
        "Literal",
        "Union",
        "Optional",
        "Annotated",
        "Final",
        "ClassVar",
        "Type",
        "Callable",
        "TypeVar",
        "Generic",
        "Protocol",
        "Self",
    }
)


def register_dependency(
    identity: DeclarationIdentity, name: str, context: SymbolContext
) -> None:
    if name in PYTHON_RESERVED_TYPE_NAMES:
        return

    context.dependencies.append(
        DependencyInformation(source=identity, target_name=name)
    )


def _find_imported(
    name: str,
    imported: list[ImportAnalysis],
) -> ImportAnalysis | None:
    for item in imported:
        if item.local_name == name:
            return item
    return None


def _retrieve_imported_symbol_id(imported_item: ImportAnalysis) -> SymbolId:
    if imported_item.kind == ImportKind.MODULE:
        return SymbolId(imported_item.imported_name)
    module_name, symbol_name = imported_item.imported_name.rsplit(".", 1)
    return SymbolId(f"{module_name}::{symbol_name}")


def _find_symbol(
    name: str,
    symbols: list[SymbolAnalysis],
) -> SymbolAnalysis | None:
    for symbol in symbols:
        if symbol.name == name:
            return symbol

    return None


def analyze_dependency(
    record: DependencyInformation,
    imported: list[ImportAnalysis],
    symbols: list[SymbolAnalysis],
) -> DependencyAnalysis | None:
    symbol_id: SymbolId
    if imported_item := _find_imported(record.target_name, imported):
        symbol_id = _retrieve_imported_symbol_id(imported_item)
        return DependencyAnalysis(
            source=record.source, target=ImportedSymbolDependency(symbol_id=symbol_id)
        )
    else:
        result = _find_symbol(record.target_name, symbols)
        if result is None:
            return None
        symbol_id = result.identity.symbol_id
        return DependencyAnalysis(
            source=record.source, target=LocalFileDependency(symbol_id=symbol_id)
        )


def resolve_dependencies(
    dependencies: list[DependencyInformation],
    imported: list[ImportAnalysis],
    symbols: list[SymbolAnalysis],
) -> dict[DeclarationIdentity, tuple[DependencyAnalysis, ...]]:
    result: dict[
        DeclarationIdentity,
        list[DependencyAnalysis],
    ] = {}

    for dependency in dependencies:
        parsed = analyze_dependency(dependency, imported, symbols)

        if parsed is None:
            continue

        result.setdefault(parsed.source, []).append(parsed)

    return {source: tuple(items) for source, items in result.items()}
