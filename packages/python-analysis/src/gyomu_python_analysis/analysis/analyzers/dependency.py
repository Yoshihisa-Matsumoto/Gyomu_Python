from gyomu_schema.schemas.python.dependency import (
    DependencyAnalysis,
    ImportedSymbolDependency,
    LocalFileDependency,
)
from gyomu_schema.schemas.python.types import DeclarationIdentity

from gyomu_python_analysis.analysis.analyzers.context import SymbolContext

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


def _has_imported_binding(name: str, context: SymbolContext) -> bool:
    return any(imported.local_name == name for imported in context.imports)


def analyze_dependency(
    identity: DeclarationIdentity, name: str, context: SymbolContext
) -> None:
    if name in context.dependency_names or name in PYTHON_RESERVED_TYPE_NAMES:
        return

    context.dependency_names.add(name)
    dependency: DependencyAnalysis
    if _has_imported_binding(name, context):
        dependency = DependencyAnalysis(
            source=identity, target=ImportedSymbolDependency(local_symbol_name=name)
        )
    else:
        dependency = DependencyAnalysis(
            source=identity, target=LocalFileDependency(local_symbol_name=name)
        )
    context.dependencies.append(dependency)
