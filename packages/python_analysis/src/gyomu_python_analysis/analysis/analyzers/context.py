from dataclasses import dataclass

from gyomu_schema.schemas.python.types import (
    DeclarationId,
    DeclarationIdentity,
    PythonPath,
    SymbolId,
)


@dataclass
class DependencyInformation:
    """Stores dependency information containing a source declaration and target name.

    Stores dependency information containing a source declaration and target name.
    """

    source: DeclarationIdentity
    """Source declaration identity."""

    target_name: str
    """Name of the target."""


@dataclass
class SymbolContext:
    """Holds contextual information about a symbol, including its dependencies,
    declaration identity, source lines, and line offsets.

    Holds contextual information about a symbol, including its dependencies, declaration
    identity, source lines, and line offsets.
    """

    dependencies: list[DependencyInformation]
    """List of dependency information items."""

    declaration: DeclarationIdentity
    """Declaration identity of the symbol."""

    source_lines: list[str]
    """Source code lines as a list of strings."""

    line_start_offsets: list[int]
    """Character offsets where each line starts."""


type MemberPath = tuple[str, ...]
"""Represents a path of member names.

Represents a path of member names.
"""


def initialize_symbol_context(
    module_name: PythonPath, name: str, source_lines: list[str]
) -> SymbolContext:
    """Initializes and returns a SymbolContext for a given module name, symbol name, and
    source lines.

    Initializes and returns a SymbolContext for a given module name, symbol name, and
    source lines.

    Args:
        module_name (PythonPath): The module name.
        name (str): The symbol name.
        source_lines (list[str]): The source code lines of the symbol.

    Returns:
        SymbolContext: The initialized SymbolContext instance.
    """
    symbol_id = build_symbol_id(module_name=module_name, name=name)
    line_start_offsets = [0]
    for line in source_lines[:-1]:
        line_start_offsets.append(
            line_start_offsets[-1] + len(line),
        )
    return SymbolContext(
        dependencies=[],
        declaration=DeclarationIdentity(
            symbol_id=symbol_id,
            declaration_id=_build_declaration_id(tuple()),
        ),
        source_lines=source_lines,
        line_start_offsets=line_start_offsets,
    )


def build_symbol_id(module_name: PythonPath, name: str) -> SymbolId:
    """Builds and returns a SymbolId from a module name and a symbol name.

    Builds and returns a SymbolId from a module name and a symbol name.

    Args:
        module_name (PythonPath): The module name.
        name (str): The symbol name.

    Returns:
        SymbolId: The constructed SymbolId.
    """
    if name == "":
        return SymbolId(f"{module_name}")
    return SymbolId(f"{module_name}::{name}")


def _build_declaration_id(member_path: MemberPath) -> DeclarationId:
    """Builds and returns a DeclarationId from a member path.

    Builds and returns a DeclarationId from a member path.

    Args:
        member_path (MemberPath): The member path.

    Returns:
        DeclarationId: The constructed DeclarationId.
    """
    if not member_path:
        return DeclarationId(".")
    return DeclarationId(".::" + "::".join(member_path))


def build_declaration_identity(
    context: SymbolContext, member_path: MemberPath
) -> DeclarationIdentity:
    """Builds and returns a DeclarationIdentity using a symbol context and a member
    path.

    Builds and returns a DeclarationIdentity using a symbol context and a member path.

    Args:
        context (SymbolContext): The symbol context.
        member_path (MemberPath): The member path.

    Returns:
        DeclarationIdentity: The constructed DeclarationIdentity.
    """
    return DeclarationIdentity(
        symbol_id=context.declaration.symbol_id,
        declaration_id=_build_declaration_id(member_path),
    )
