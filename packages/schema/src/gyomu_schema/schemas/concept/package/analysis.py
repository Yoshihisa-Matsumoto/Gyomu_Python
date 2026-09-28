from typing import Literal

from gyomu_schema.schemas.concept.directory.concept import DirectoryConcept
from gyomu_schema.schemas.concept.file_summary import FileSummary
from gyomu_schema.schemas.python.types import ProjectRelativePath
from pydantic import BaseModel


class PyProjectAnalysis(BaseModel):
    name: str

    version: str
    license: str


class DirectoryAnalysisFact(BaseModel):
    public_symbol_count: int
    file_count: int
    total_symbol_count: int


class DirectoryAnalysis(BaseModel):
    path: ProjectRelativePath
    concept: DirectoryConcept
    fact: DirectoryAnalysisFact


DependencyKind = Literal["version", "workspace", "catalog"]
DependencySource = Literal["dependency", "devDependency"]


class DependencyAnalysis(BaseModel):
    package_name: str
    kind: DependencyKind
    source: DependencySource
    required_version: str | None


class PackageAnalysis(BaseModel):
    package: PyProjectAnalysis
    dependencies: tuple[DependencyAnalysis, ...]
    directories: tuple[DirectoryAnalysis, ...]
    public_files: tuple[FileSummary, ...]
