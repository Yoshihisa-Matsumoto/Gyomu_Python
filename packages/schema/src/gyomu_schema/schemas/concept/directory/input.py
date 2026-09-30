from pydantic import BaseModel

from gyomu_schema.schemas.concept.directory.concept import DirectoryConcept
from gyomu_schema.schemas.concept.file_summary import FileSummary
from gyomu_schema.schemas.python.types import DirectoryRelativePath


class SubDirectoryInput(BaseModel):
    """Defines input data for a subdirectory, including its path and directory
    concept.
    """

    path: DirectoryRelativePath
    """Relative path of the subdirectory."""

    concept: DirectoryConcept
    """Concept associated with the subdirectory."""


class DirectoryConceptInput(BaseModel):
    """Defines input data for a directory concept, containing files and
    subdirectories.
    """

    files: tuple[FileSummary, ...]
    """Collection of file summaries within the directory."""

    sub_directories: tuple[SubDirectoryInput, ...]
    """Collection of subdirectory inputs within the directory."""
