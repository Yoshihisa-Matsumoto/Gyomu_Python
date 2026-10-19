from gyomu_schema.schemas.python.import_analysis import ImportKind
from gyomu_schema.schemas.python.module import ModuleAnalysis
from gyomu_schema.schemas.python.types import PythonPath, SymbolId

from gyomu_python_analysis.analysis.query import find_symbol_by_name
from gyomu_python_analysis.analysis.resolve.models import ResolvedReference


def _is_dotted_name(value: str) -> bool:
    """Return whether the value is a dot-separated sequence of identifiers."""
    return bool(value) and all(part.isidentifier() for part in value.split("."))


def resolve_reference(
    reference_name: str,
    module: ModuleAnalysis,
) -> ResolvedReference | None:
    """Resolve a reference using imports and symbols in a module.

    Args:
        reference_name: A simple or dotted name from source code.
        module: The module containing the reference.

    Returns:
        The resolved reference. if not found, return None

    """
    if not _is_dotted_name(reference_name):
        return None

    candidates = sorted(
        (
            imp
            for imp in module.imports
            if _is_dotted_name(imp.local_name)
            and (
                reference_name == imp.local_name
                or reference_name.startswith(f"{imp.local_name}.")
            )
        ),
        key=lambda imp: len(imp.local_name),
        reverse=True,
    )

    for imp in candidates:
        if imp.kind == ImportKind.SYMBOL:
            if reference_name != imp.local_name:
                continue

            symbol_id = imp.get_symbol_id()
            if symbol_id is None:
                continue

            return ResolvedReference(
                import_analysis=imp,
                module_path=imp.get_module_path(),
                symbol_id=symbol_id,
            )

        if imp.kind == ImportKind.MODULE:
            if imp.imported_name.startswith(f"{imp.local_name}."):
                # `import package.submodule` binds `package`.
                if (
                    reference_name != imp.imported_name
                    and not reference_name.startswith(f"{imp.imported_name}.")
                ):
                    continue

                canonical_name = reference_name
                module_path = PythonPath(imp.imported_name)
            else:
                suffix = reference_name[len(imp.local_name) :]
                canonical_name = f"{imp.imported_name}{suffix}"
                module_path = PythonPath(imp.imported_name)

            if canonical_name == module_path:
                return ResolvedReference(
                    import_analysis=imp,
                    module_path=module_path,
                    symbol_id=None,
                )

            prefix = f"{module_path}."
            if not canonical_name.startswith(prefix):
                continue

            symbol_name = canonical_name[len(prefix) :]
            if not symbol_name.isidentifier():
                continue

            return ResolvedReference(
                import_analysis=imp,
                module_path=module_path,
                symbol_id=SymbolId(f"{module_path}::{symbol_name}"),
            )

    # If no import matches, look for a symbol defined in this module.
    symbol = find_symbol_by_name(reference_name, module)
    if symbol is not None:
        module_path = module.module_name
        return ResolvedReference(
            import_analysis=None,
            module_path=module_path,
            symbol_id=SymbolId(f"{module_path}::{symbol.name}"),
        )

    return None
