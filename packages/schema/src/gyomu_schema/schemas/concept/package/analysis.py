from typing import Literal, Self

from pydantic import BaseModel

from gyomu_schema.schemas.concept.directory.concept import DirectoryConcept
from gyomu_schema.schemas.concept.file_summary import FileSummary
from gyomu_schema.schemas.python.types import ProjectRelativePath


class PyProjectAnalysis(BaseModel):
    """Defines a PyProject configuration analysis containing package name,
    description, version, and license.
    """

    name: str
    """The name of the package."""

    description: str | None
    """The description of the package, if available."""

    version: str
    """The version string of the package."""

    license: str
    """The license identifier or text for the package."""


class DirectoryAnalysisFact(BaseModel):
    """Defines directory analysis metrics containing public symbol count, file count,
    and total symbol count.
    """

    public_symbol_count: int
    """The number of public symbols in the directory."""

    file_count: int
    """The number of files in the directory."""

    total_symbol_count: int
    """The total number of symbols in the directory."""

    def add(self, item: Self) -> Self:
        """Combines another directory analysis fact into this instance.

        Args:
            item (Self): Another directory analysis fact to add.

        Returns:
            Self: The updated directory analysis fact instance.
        """
        self.public_symbol_count += item.public_symbol_count
        self.file_count += item.file_count
        self.total_symbol_count += item.total_symbol_count
        return self


class DirectoryAnalysis(BaseModel):
    """Defines a directory analysis containing its path, concept, and factual
    metrics.
    """

    path: ProjectRelativePath
    """The relative path of the directory."""

    concept: DirectoryConcept
    """The directory concept classification."""

    fact: DirectoryAnalysisFact
    """The analytical facts and metrics for the directory."""


PackageDependencyKind = Literal["version", "workspace", "catalog"]
"""Defines the kind of package dependency (version, workspace, or catalog)."""

PackageDependencySource = Literal["dependency", "devDependency"]
"""Defines the source of package dependency (dependency or devDependency)."""


class PackageDependencyAnalysis(BaseModel):
    """Defines package dependency analysis containing package name, kind, source, and
    required version.
    """

    package_name: str
    """The name of the dependency package."""

    kind: PackageDependencyKind
    """The kind of dependency."""

    source: PackageDependencySource
    """The source configuration section for the dependency."""

    required_version: str | None
    """The required version specification, if specified."""


class PackageAnalysis(BaseModel):
    """Defines comprehensive package analysis containing package metadata,
    dependencies, directories, and public files.
    """

    package: PyProjectAnalysis
    """The pyproject analysis metadata for the package."""

    dependencies: tuple[PackageDependencyAnalysis, ...]
    """A tuple of package dependency analyses."""

    directories: tuple[DirectoryAnalysis, ...]
    """A tuple of directory analyses within the package."""

    public_files: tuple[FileSummary, ...]
    """A tuple of summaries for public files in the package."""
