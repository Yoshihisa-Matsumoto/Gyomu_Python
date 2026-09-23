from dataclasses import dataclass

from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.snapshot.models import ProjectSnapshot
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.schemas.types import FullPath
from pydantic import BaseModel, Field


class FileFilter(BaseModel):
    pattern: str


class SnapshotTargetOption(BaseModel):
    all: bool = Field(default=False)
    file_filter: FileFilter | None = Field(default=None)


class DocstringExecutionOption(BaseModel):
    enabled: bool = Field(default=True)
    log_keyword: str | None = Field(default=None)


class SnapshotActionOption(BaseModel):
    docstring: DocstringExecutionOption
    project_context: bool = Field(default=False)
    unit_test: bool = Field(default=False)


class SnapshotExecutionOption(BaseModel):
    commit: bool
    target: SnapshotTargetOption
    action: SnapshotActionOption


@dataclass(frozen=True)
class SnapshotRequest:
    repository_root_path: FullPath
    project_context: ProjectContext
    option: SnapshotExecutionOption


class SnapshotTarget(BaseModel):
    files: frozenset[ProjectRelativePath]
    deleted_files: frozenset[ProjectRelativePath]
    snapshot: ProjectSnapshot
