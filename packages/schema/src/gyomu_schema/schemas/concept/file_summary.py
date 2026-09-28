from gyomu_schema.schemas.python.symbol_base import DeclarationKind
from gyomu_schema.schemas.python.types import ProjectRelativePath
from pydantic import BaseModel


class PublicDeclarationSummary(BaseModel):
    symbol: str
    kind: DeclarationKind
    summary: str


class DependencySummary(BaseModel):
    target: str
    external: bool


class FileSummary(BaseModel):
    path: ProjectRelativePath
    exports: tuple[PublicDeclarationSummary, ...]
    dependencies: tuple[DependencySummary, ...]
