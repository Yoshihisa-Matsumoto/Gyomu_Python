from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from gyomu_schema.schemas.python.types import ProjectRelativePath, WorkspaceRelativePath


class FileSnapshot(BaseModel):
    """Represents a snapshot of an individual file containing its relative path,
    content hash, and modification timestamp.
    """

    project_relative_path: ProjectRelativePath
    """The project-relative path of the file."""

    raw_hash: str
    """The raw content hash of the file."""

    modified_at: datetime
    """The timestamp when the file was last modified."""


class ProjectSnapshot(BaseModel):
    """Represents a snapshot of a project containing its root path and a collection
    of file snapshots.
    """

    project_root: WorkspaceRelativePath
    """The workspace-relative path of the project root."""

    files: tuple[FileSnapshot, ...]
    """A collection of file snapshots belonging to the project."""


class FileAdded(BaseModel):
    """Represents the addition of a new file in the project."""

    project_relative_path: ProjectRelativePath
    """The project-relative path of the added file."""

    current: FileSnapshot
    """The current file snapshot."""

    type: Literal["added"] = "added"
    """The change type discriminator, set to 'added'."""


class FileUpdated(BaseModel):
    """Represents an update to an existing file in the project."""

    project_relative_path: ProjectRelativePath
    """The project-relative path of the updated file."""

    previous: FileSnapshot
    """The previous file snapshot before the update."""

    current: FileSnapshot
    """The current file snapshot after the update."""

    type: Literal["updated"] = "updated"
    """The change type discriminator, set to 'updated'."""


class FileDeleted(BaseModel):
    """Represents the deletion of a file from the project."""

    project_relative_path: ProjectRelativePath
    """The project-relative path of the deleted file."""

    previous: FileSnapshot
    """The previous file snapshot before deletion."""

    type: Literal["deleted"] = "deleted"
    """The change type discriminator, set to 'deleted'."""


type FileChange = FileAdded | FileUpdated | FileDeleted
"""Represents any file change event (added, updated, or deleted)."""
