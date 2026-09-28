from dataclasses import dataclass

from gyomu_schema.schemas.snapshot.types import FileChange, ProjectSnapshot
from gyomu_schema.schemas.types import FullPath


@dataclass
class AnalyzeProjectChangesResult:
    """Represents the result of analyzing project changes, containing project
    identification, snapshot paths, previous and current snapshots, and file
    differences.
    """

    project_id: str
    """The identifier of the analyzed project."""

    snapshot_path: FullPath
    """The full path to the snapshot storage or record."""

    previous_snapshot: ProjectSnapshot | None
    """The previous project snapshot, or None if this is the initial snapshot."""

    current_snapshot: ProjectSnapshot
    """The current project snapshot."""

    diff: tuple[FileChange, ...]
    """A tuple of file changes detected between the previous and current snapshots."""
