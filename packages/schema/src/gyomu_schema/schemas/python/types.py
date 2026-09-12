from collections.abc import Hashable
from pathlib import Path
from typing import NewType

from pydantic import BaseModel, ConfigDict

DirectoryRelativePath = NewType("DirectoryRelativePath", Path)

ProjectRelativePath = NewType("ProjectRelativePath", Path)

SourceRelativePath = NewType("SourceRelativePath", Path)

PythonPath = NewType("PythonPath", str)

WorkspaceRelativePath = NewType("WorkspaceRelativePath", Path)

DeclarationId = NewType("DeclarationId", str)

SymbolId = NewType("SymbolId", str)


class DeclarationIdentity(BaseModel, Hashable):
    """
    Gyomu Context:
        - symbol_id identifies the externally referenceable Symbol
        that owns the declaration.
        It uses the format "<module_name>::<symbol_name>" and
        is shared by all declarations
        belonging to the same Symbol.

        For example:
            gyomu_schema.schemas.python.user::User

        For a class Symbol, the same symbol_id is used for its variables,
          methods, nested classes, method parameters, and return values.

        - declaration_id identifies a declaration within the Symbol.
        It starts with the "." and then
        represents the declaration's access path.

        Normal declarations are represented directly as an access path:
            .
            .::name
            .::get_name
            .::Address
            .::Address::to_string

        Special declarations whose meaning cannot be expressed unambiguously by a normal
        access path use a "$" marker:
            .::get_name::$parameter::user_id
            .::get_name::$return

        The "$" marker is used only for such special declaration kinds, not for every
        path segment.
    """

    symbol_id: SymbolId
    declaration_id: DeclarationId

    model_config = ConfigDict(frozen=True)

    def __hash__(self) -> int:
        return hash((self.symbol_id, self.declaration_id))


def is_declaration_identity_equal(
    a: DeclarationIdentity, b: DeclarationIdentity
) -> bool:
    return a.symbol_id == b.symbol_id and a.declaration_id == b.declaration_id
