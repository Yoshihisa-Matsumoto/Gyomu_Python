from typing import Literal, Self

from gyomu_schema.schemas.concept.directory.concept import DirectoryConcept
from gyomu_schema.schemas.concept.file_summary import FileSummary
from gyomu_schema.schemas.python.types import ProjectRelativePath
from pydantic import BaseModel


class PyProjectAnalysis(BaseModel):
    name: str
    description: str | None
    version: str
    license: str


class DirectoryAnalysisFact(BaseModel):
    public_symbol_count: int
    file_count: int
    total_symbol_count: int

    def add(self, item: Self) -> Self:
        self.public_symbol_count += item.public_symbol_count
        self.file_count += item.file_count
        self.total_symbol_count += item.total_symbol_count
        return self


class DirectoryAnalysis(BaseModel):
    path: ProjectRelativePath
    concept: DirectoryConcept
    fact: DirectoryAnalysisFact


PackageDependencyKind = Literal["version", "workspace", "catalog"]
PackageDependencySource = Literal["dependency", "devDependency"]


class PackageDependencyAnalysis(BaseModel):
    package_name: str
    kind: PackageDependencyKind
    source: PackageDependencySource
    required_version: str | None


class PackageAnalysis(BaseModel):
    package: PyProjectAnalysis
    dependencies: tuple[PackageDependencyAnalysis, ...]
    directories: tuple[DirectoryAnalysis, ...]
    public_files: tuple[FileSummary, ...]
