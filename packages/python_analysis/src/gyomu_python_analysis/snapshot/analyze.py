from gyomu_infra.filesystem.file_io import read_json
from gyomu_schema.schemas.python.types import WorkspaceRelativePath
from gyomu_schema.schemas.types import FullPath
from returns.result import Failure, Result, Success

from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.snapshot.create import create_snapshot
from gyomu_python_analysis.snapshot.diff import diff_snapshot
from gyomu_python_analysis.snapshot.models import (
    AnalyzeProjectChangesResult,
    ProjectSnapshot,
)
from gyomu_python_analysis.snapshot.project import ensure_project_workspace


def analyze_project_changes(
    repository_root_path: FullPath,
    project_context: ProjectContext,
    *,
    include_all: bool = False,
) -> Result[AnalyzeProjectChangesResult, AnalysisError]:
    project_path = WorkspaceRelativePath(
        project_context.project_root.relative_to(repository_root_path)
    )
    result = ensure_project_workspace(repository_root_path, project_path)
    if isinstance(result, Failure):
        return result
    project = result.unwrap()

    previous_snapshot: ProjectSnapshot = ProjectSnapshot(
        project_root=project_path, files=tuple()
    )
    use_snapshot = project.snapshot_path.exists() and not include_all
    if use_snapshot:
        result = read_json(path=project.snapshot_path, model_type=ProjectSnapshot).alt(
            lambda err: AnalysisError(
                "fail to read project snapshot",
                file_path=project.snapshot_path,
                phase="snapshot",
                context="gyomu_python_analysis.snapshot.analyze.analyze_project_changes",
            ).chain(err)
        )
        if isinstance(result, Failure):
            return result
        previous_snapshot = result.unwrap()

    result = create_snapshot(project_context=project_context, project_path=project_path)
    if isinstance(result, Failure):
        return result
    current_snapshot = result.unwrap()

    diff = diff_snapshot(previous=previous_snapshot, current=current_snapshot)

    return Success(
        AnalyzeProjectChangesResult(
            project_id=project.project_id,
            snapshot_path=project.snapshot_path,
            previous_snapshot=previous_snapshot if use_snapshot else None,
            current_snapshot=current_snapshot,
            diff=diff,
        )
    )
