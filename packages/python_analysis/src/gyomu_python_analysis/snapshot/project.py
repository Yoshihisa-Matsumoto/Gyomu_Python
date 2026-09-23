from gyomu_infra.filesystem.file_io import ensure_directory
from gyomu_infra.hash.hash import short_sha256
from gyomu_schema.schemas.python.types import WorkspaceRelativePath
from gyomu_schema.schemas.types import FullPath
from pydantic import BaseModel
from returns.result import Failure, Result, Success

from gyomu_python_analysis.error.analysis import AnalysisError


def to_project_id(project_path: WorkspaceRelativePath) -> str:
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
    snapshot_root_path: FullPath
    snapshot_path: FullPath


def ensure_project_workspace(
    repository_root_path: FullPath, project_path: WorkspaceRelativePath
) -> Result[ProjectSnapshotWorkspace, AnalysisError]:
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
