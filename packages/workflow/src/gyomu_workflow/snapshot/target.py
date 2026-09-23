from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.snapshot.analyze import analyze_project_changes
from gyomu_python_analysis.snapshot.models import FileDeleted
from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.schemas.types import FullPath
from gyomu_schema.utility.context import caller_context
from returns.result import Failure, Result, Success

from gyomu_workflow.snapshot.models import SnapshotTarget, SnapshotTargetOption


def resolve_snapshot_target(
    repository_root_path: FullPath,
    project_context: ProjectContext,
    option: SnapshotTargetOption,
) -> Result[SnapshotTarget, GyomuError]:

    result = analyze_project_changes(
        repository_root_path=repository_root_path,
        project_context=project_context,
        include_all=option.all,
    )
    if isinstance(result, Failure):
        context = caller_context()
        return result.alt(
            lambda error: GyomuError(
                message="fail to analyze project change",
                domain="snapshot",
                operation="resolve_snapshot_target",
                reason="external_failure",
                context=context,
            ).chain(error)
        )
    change_result = result.unwrap()

    if not option.file_filter:
        diff = change_result.diff
        return Success(
            SnapshotTarget(
                files=frozenset(
                    change.project_relative_path
                    for change in diff
                    if not isinstance(change, FileDeleted)
                ),
                deleted_files=frozenset(
                    change.project_relative_path
                    for change in diff
                    if isinstance(change, FileDeleted)
                ),
                snapshot=change_result.current_snapshot,
            )
        )
    else:
        return Success(
            SnapshotTarget(
                deleted_files=frozenset(),
                files=filter_included_files(
                    project_context.included_files,
                    option.file_filter.pattern,
                ),
                snapshot=change_result.current_snapshot,
            )
        )


def filter_included_files(
    included_files: frozenset[ProjectRelativePath],
    path: str,
) -> frozenset[ProjectRelativePath]:
    return frozenset(
        (
            included_file
            for included_file in included_files
            if included_file.match(path)
        ),
    )
