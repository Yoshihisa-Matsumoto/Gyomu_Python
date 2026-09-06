from dataclasses import dataclass

from gyomu_schema.schemas.python.dependency import DependencyAnalysis
from gyomu_schema.schemas.python.import_analysis import ImportAnalysis
from gyomu_schema.schemas.python.types import (
    DeclarationId,
    DeclarationIdentity,
    PythonPath,
    SymbolId,
)


@dataclass
class SymbolContext:
    dependencies: list[DependencyAnalysis]
    dependency_names: set[str]
    imports: tuple[ImportAnalysis, ...]
    symbol_id: SymbolId


type MemberPath = tuple[str, ...]


def initialize_symbol_context(
    imports: tuple[ImportAnalysis, ...], module_name: PythonPath, name: str
) -> SymbolContext:
    return SymbolContext(
        dependencies=[],
        dependency_names=set(),
        imports=imports,
        symbol_id=build_symbol_id(module_name=module_name, name=name),
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
        symbol_id=context.symbol_id,
        declaration_id=_build_declaration_id(member_path),
    )
