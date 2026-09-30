from gyomu_schema.schemas.concept.directory.concept import DirectoryImportance
from gyomu_schema.schemas.concept.package.analysis import PyProjectAnalysis
from gyomu_schema.schemas.python.types import ProjectRelativePath
from pydantic import BaseModel


class PublicApiSymbol(BaseModel):
    """Defines a public API symbol with its name and summary."""

    name: str
    """The name of the public API symbol."""

    summary: str
    """A summary describing the public API symbol."""


class PublicSymbolsModule(BaseModel):
    """Defines public symbols belonging to a module."""

    module: str
    """The module name."""

    symbols: tuple[PublicApiSymbol, ...]
    """The collection of public API symbols in the module."""


class TopDirectory(BaseModel):
    """Defines a top-level directory with its path, importance, summary, and
    responsibilities.
    """

    path: ProjectRelativePath
    """The project-relative path of the top-level directory."""

    importance: DirectoryImportance
    """The importance level of the directory."""

    summary: str
    """A summary describing the top-level directory."""

    responsibilities: tuple[str, ...]
    """The responsibilities assigned to the top-level directory."""


class PackageDependencyInput(BaseModel):
    """Defines a package dependency with its name and version."""

    package_name: str
    """The name of the dependent package."""

    version: str
    """The version requirement of the dependent package."""


class PackageConceptInput(BaseModel):
    """Defines input data for the package concept pipeline, including package
    analysis, top directories, public symbols, and dependencies.
    """

    package: PyProjectAnalysis
    """The pyproject analysis of the package."""

    top_directories: tuple[TopDirectory, ...]
    """The top-level directories of the package."""

    public_symbols: tuple[PublicSymbolsModule, ...]
    """The public symbols organized by module."""

    dependencies: tuple[PackageDependencyInput, ...]
    """The package dependencies."""
