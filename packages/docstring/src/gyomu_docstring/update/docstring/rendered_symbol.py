from gyomu_schema.schemas.python.location import SourceLocation
from gyomu_schema.schemas.python.types import DeclarationIdentity
from pydantic import BaseModel


class RenderedSymbolDocstring(BaseModel):
    identity: DeclarationIdentity
    docstring: str | None
    location: SourceLocation
