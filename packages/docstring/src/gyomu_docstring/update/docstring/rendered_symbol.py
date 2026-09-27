from gyomu_schema.schemas.python.location import SourceLocation
from gyomu_schema.schemas.python.types import DeclarationIdentity
from pydantic import BaseModel


class RenderedSymbolDocstring(BaseModel):
    """Represents a rendered docstring with its identity, content, and source
    location.
    """

    identity: DeclarationIdentity
    """The declaration identity."""

    docstring: str | None
    """The rendered docstring content, if any."""

    location: SourceLocation
    """The source location of the declaration."""
