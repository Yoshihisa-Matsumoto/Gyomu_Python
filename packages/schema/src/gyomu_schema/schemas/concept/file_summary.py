from gyomu_schema.schemas.python.symbol_base import DeclarationKind
from gyomu_schema.schemas.python.types import ProjectRelativePath
from pydantic import BaseModel


class PublicDeclarationSummary(BaseModel):
    symbol: str
    kind: DeclarationKind
    summary: str


# class ReExportSummarySingle(BaseModel):
#     module: str
#     export_all: Literal[False] = False
#     symbol: str


# class ReExportSummaryAll(BaseModel):
#     module: str
#     export_all: Literal[True] = True


# type ReExportSummary = ReExportSummaryAll | ReExportSummarySingle


class DependencySummary(BaseModel):
    target: str
    external: bool


class FileSummary(BaseModel):
    path: ProjectRelativePath
    exports: tuple[PublicDeclarationSummary, ...]
    # re_exports: tuple[ReExportSummary, ...]
    dependencies: tuple[DependencySummary, ...]
