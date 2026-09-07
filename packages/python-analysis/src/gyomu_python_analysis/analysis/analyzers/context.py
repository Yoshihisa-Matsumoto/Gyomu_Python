from dataclasses import dataclass

from gyomu_schema.schemas.python.types import (
    DeclarationId,
    DeclarationIdentity,
    PythonPath,
    SymbolId,
)


@dataclass
class DependencyInformation:
    source: DeclarationIdentity
    target_name: str


@dataclass
class SymbolContext:
    dependencies: list[DependencyInformation]
    declaration: DeclarationIdentity


type MemberPath = tuple[str, ...]


def initialize_symbol_context(module_name: PythonPath, name: str) -> SymbolContext:
    symbol_id = build_symbol_id(module_name=module_name, name=name)
    return SymbolContext(
        dependencies=[],
        declaration=DeclarationIdentity(
            symbol_id=symbol_id,
            declaration_id=_build_declaration_id(tuple()),
        ),
    )


def build_symbol_id(module_name: PythonPath, name: str) -> SymbolId:
    if name == "":
        return SymbolId(f"{module_name}")
    return SymbolId(f"{module_name}::{name}")


def _build_declaration_id(member_path: MemberPath) -> DeclarationId:
    if not member_path:
        return DeclarationId(".")
    return DeclarationId(".::" + "::".join(member_path))


def build_declaration_identity(
    context: SymbolContext, member_path: MemberPath
) -> DeclarationIdentity:
    return DeclarationIdentity(
        symbol_id=context.declaration.symbol_id,
        declaration_id=_build_declaration_id(member_path),
    )
