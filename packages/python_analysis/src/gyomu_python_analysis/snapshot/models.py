from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from gyomu_schema.schemas.python.types import ProjectRelativePath, WorkspaceRelativePath
from gyomu_schema.schemas.types import FullPath
from pydantic import BaseModel


class FileSnapshot(BaseModel):
    project_relative_path: ProjectRelativePath
    raw_hash: str
    modified_at: datetime


class ProjectSnapshot(BaseModel):
    project_root: WorkspaceRelativePath
    files: tuple[FileSnapshot, ...]


class FileAdded(BaseModel):
    project_relative_path: ProjectRelativePath
    current: FileSnapshot
    type: Literal["added"] = "added"


class FileUpdated(BaseModel):
    project_relative_path: ProjectRelativePath
    previous: FileSnapshot
    current: FileSnapshot
    type: Literal["updated"] = "updated"


class FileDeleted(BaseModel):
    project_relative_path: ProjectRelativePath
    previous: FileSnapshot
    type: Literal["deleted"] = "deleted"


type FileChange = FileAdded | FileUpdated | FileDeleted


@dataclass
class AnalyzeProjectChangesResult:
    project_id: str
    snapshot_path: FullPath
    previous_snapshot: ProjectSnapshot | None
    current_snapshot: ProjectSnapshot
    diff: tuple[FileChange, ...]
