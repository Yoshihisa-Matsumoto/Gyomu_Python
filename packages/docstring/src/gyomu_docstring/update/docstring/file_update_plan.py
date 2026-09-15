from gyomu_schema.schemas.python.location import SourceLocation
from gyomu_schema.schemas.python.types import DeclarationIdentity
from pydantic import BaseModel


class FileUpdatePlanEntry(BaseModel):
    identity: DeclarationIdentity
    location: SourceLocation
    new_text: str


class FileUpdatePlan(BaseModel):
    items: tuple[FileUpdatePlanEntry, ...]
