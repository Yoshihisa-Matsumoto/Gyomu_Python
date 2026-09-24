from collections.abc import Hashable
from pathlib import Path
from typing import NewType

from pydantic import BaseModel, ConfigDict

DirectoryRelativePath = NewType("DirectoryRelativePath", Path)
"""Represents a directory-relative path."""


ProjectRelativePath = NewType("ProjectRelativePath", Path)
"""Represents a project-relative path."""


SourceRelativePath = NewType("SourceRelativePath", Path)
"""Represents a source-relative path."""


PythonPath = NewType("PythonPath", str)
"""Represents a Python path string."""


WorkspaceRelativePath = NewType("WorkspaceRelativePath", Path)
"""Represents a workspace-relative path."""


DeclarationId = NewType("DeclarationId", str)
"""Represents a declaration identifier string."""


SymbolId = NewType("SymbolId", str)
"""Represents a symbol identifier string."""


class DeclarationIdentity(BaseModel, Hashable):
    """Represents a unique identity for a declaration within Gyomu context.

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
    """The symbol ID component of the declaration identity."""

    declaration_id: DeclarationId
    """The declaration ID component of the declaration identity."""

    model_config = ConfigDict(frozen=True)

    def __hash__(self) -> int:
        """Computes the hash of the declaration identity.

        Returns:
            int: Hash value of the declaration identity.
        """
        return hash((self.symbol_id, self.declaration_id))


def is_declaration_identity_equal(
    a: DeclarationIdentity, b: DeclarationIdentity
) -> bool:
    """Checks whether two declaration identities are equal.

    Args:
        a (DeclarationIdentity): First declaration identity to compare.
        b (DeclarationIdentity): Second declaration identity to compare.

    Returns:
        bool: True if both declaration identities are equal, false otherwise.
    """
    return a.symbol_id == b.symbol_id and a.declaration_id == b.declaration_id
