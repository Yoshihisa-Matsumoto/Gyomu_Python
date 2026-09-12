from dataclasses import dataclass

from gyomu_schema.schemas.python.location import SourceLocation
from gyomu_schema.schemas.python.types import DeclarationIdentity


@dataclass
class FileUpdatePlanEntry:
    identity: DeclarationIdentity
    location: SourceLocation
    new_text: str


@dataclass
class FileUpdatePlan:
    items: tuple[FileUpdatePlanEntry, ...]
