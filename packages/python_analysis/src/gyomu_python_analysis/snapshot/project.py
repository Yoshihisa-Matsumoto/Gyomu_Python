from gyomu_infra.filesystem.file_io import ensure_directory
from gyomu_infra.hash.hash import short_sha256
from gyomu_schema.schemas.python.types import WorkspaceRelativePath
from gyomu_schema.schemas.types import FullPath
from pydantic import BaseModel
from returns.result import Failure, Result, Success

from gyomu_python_analysis.error.analysis import AnalysisError


def to_project_id(project_path: WorkspaceRelativePath) -> str:
    """Derives a unique project identifier from a workspace-relative path.

    Derives a unique project identifier from a workspace-relative path.

    Args:
        project_path (WorkspaceRelativePath): Workspace-relative path of the project

    Returns:
        str: Unique project identifier string
    """
    return short_sha256(str(project_path))


class ProjectSnapshotWorkspace(BaseModel):
    """Filesystem workspace for snapshots of a project.

    Gyomu Context:
        This structure contains the resolved paths required to create,
        persist, and compare snapshots for a project within a workspace.

        The project ID is derived from the project's workspace-relative path.
        Consequently, moving a project to a different path creates a new
        snapshot identity and does not reuse the previous snapshot.
    """

    project_id: str
    """Unique project identifier.

    Unique project identifier.
    """
    snapshot_root_path: FullPath
    """Root directory path for project snapshots.

    Root directory path for project snapshots.
    """
    snapshot_path: FullPath
    """File path for the snapshot hash data.

    File path for the snapshot hash data.
    """


def ensure_project_workspace(
    repository_root_path: FullPath, project_path: WorkspaceRelativePath
) -> Result[ProjectSnapshotWorkspace, AnalysisError]:
    """Ensures and initializes the filesystem workspace for project snapshots.

    Ensures and initializes the filesystem workspace for project snapshots.

    Args:
        repository_root_path (FullPath): Root path of the repository
        project_path (WorkspaceRelativePath): Workspace-relative path of the project

    Returns:
        Result[ProjectSnapshotWorkspace, AnalysisError]: Success with
            ProjectSnapshotWorkspace or Failure with AnalysisError
    """
    project_id = to_project_id(project_path)
    project_root_path = FullPath(
        repository_root_path / ".gyomu" / "snapshot" / project_id
    )
    snapshot_path = FullPath(project_root_path / "file-hashes.json")
    result = ensure_directory(snapshot_path.parent)

    if isinstance(result, Failure):
        return Failure(
            AnalysisError(
                message="fail to prepare project snapshot folder",
                file_path=snapshot_path.parent,
                phase="snapshot",
                context="gyomu_python_analysis.snapshot.project.ensure_workspace",
            ).chain(result.failure())
        )
    return Success(
        ProjectSnapshotWorkspace(
            project_id=project_id,
            snapshot_root_path=project_root_path,
            snapshot_path=snapshot_path,
        )
    )
