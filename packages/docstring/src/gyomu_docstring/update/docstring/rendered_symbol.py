from dataclasses import dataclass

from gyomu_schema.schemas.python.location import SourceLocation
from gyomu_schema.schemas.python.types import DeclarationIdentity


@dataclass
class RenderedSymbolDocstring:
    identity: DeclarationIdentity
    docstring: str | None
    location: SourceLocation
