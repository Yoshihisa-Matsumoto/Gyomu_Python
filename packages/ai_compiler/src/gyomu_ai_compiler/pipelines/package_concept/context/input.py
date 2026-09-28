from gyomu_schema.schemas.concept.directory.concept import DirectoryImportance
from gyomu_schema.schemas.concept.package.analysis import PyProjectAnalysis
from gyomu_schema.schemas.python.types import ProjectRelativePath
from pydantic import BaseModel


class PublicApiSymbol(BaseModel):
    name: str
    summary: str


class PublicApiModule(BaseModel):
    module: str
    symbols: tuple[PublicApiSymbol, ...]


class TopDirectory(BaseModel):
    path: ProjectRelativePath
    importance: DirectoryImportance
    summary: str
    responsibilities: tuple[str, ...]


class PackageDependencyInput(BaseModel):
    package_name: str
    version: str


class PackageConceptInput(BaseModel):
    package: PyProjectAnalysis
    top_directories: tuple[TopDirectory, ...]
    public_api: tuple[PublicApiModule, ...]
    dependencies: tuple[PackageDependencyInput, ...]
