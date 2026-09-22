from collections import Counter

from gyomu_infra.filesystem.file_io import write_json
from gyomu_infra.logger import logger
from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.snapshot.create import create_snapshot
from gyomu_python_analysis.snapshot.diff import diff_snapshot
from gyomu_python_analysis.snapshot.models import ProjectSnapshot
from gyomu_python_analysis.snapshot.project import ensure_project_workspace
from gyomu_schema.schemas.python.types import WorkspaceRelativePath
from gyomu_schema.schemas.types import FullPath
from returns.result import Failure, Result


def commit_project_changes(
    repository_root_path: FullPath,
    project_context: ProjectContext,
    expected_snapshot: ProjectSnapshot,
) -> Result[None, AnalysisError]:
    project_path = WorkspaceRelativePath(
        project_context.project_root.relative_to(repository_root_path)
    )
    result = ensure_project_workspace(repository_root_path, project_path)
    if isinstance(result, Failure):
        return result
    project = result.unwrap()

    result = create_snapshot(project_context=project_context, project_path=project_path)
    if isinstance(result, Failure):
        return result
    current_snapshot = result.unwrap()

    diff = diff_snapshot(previous=expected_snapshot, current=current_snapshot)
    if diff:
        logger.error("Snapshot diff exists. Someone modified unexpectedly")
        logger.error_object(diff)
        change_counts = Counter(entry.type for entry in diff)
        return Failure(
            AnalysisError(
                message=(
                    "Snapshot diff detected. Project was modified during execution."
                ),
                file_path=project_context.project_root,
                phase="snapshot",
                context="gyomu_python_analysis.snapshot.commit.commit_project_changes",
                details={
                    "added": change_counts["added"],
                    "updated": change_counts["updated"],
                    "deleted": change_counts["deleted"],
                },
            )
        )

    return write_json(
        path=project.snapshot_path, value_type=ProjectSnapshot, value=current_snapshot
    ).alt(
        lambda err: AnalysisError(
            "fail to write project snapshot",
            file_path=project.snapshot_path,
            phase="snapshot",
            context="gyomu_python_analysis.snapshot.commit.commit_project_changes",
        ).chain(err)
    )
