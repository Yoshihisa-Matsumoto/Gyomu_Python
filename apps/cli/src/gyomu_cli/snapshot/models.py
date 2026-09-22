from dataclasses import dataclass

from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.schemas.types import FullPath


@dataclass(frozen=True)
class FileFilter:
    pattern: str


@dataclass(frozen=True)
class SnapshotExecutionOption:
    commit: bool
    docstring: bool = True
    all: bool = False
    file_filter: FileFilter | None = None
    project_context: bool = False
    unit_test: bool = False
    log_keyword: str | None = None


@dataclass(frozen=True)
class SnapshotRequest:
    repository_root_path: FullPath
    project_context: ProjectContext
    option: SnapshotExecutionOption
