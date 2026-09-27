from gyomu_schema.schemas.concept.directory.concept import DirectoryConcept
from gyomu_schema.schemas.concept.file_summary import FileSummary
from gyomu_schema.schemas.python.types import DirectoryRelativePath
from pydantic import BaseModel


class SubDirectoryInput(BaseModel):
    path: DirectoryRelativePath
    concept: DirectoryConcept


class DirectoryConceptInput(BaseModel):
    files: tuple[FileSummary, ...]
    sub_directories: tuple[SubDirectoryInput, ...]
