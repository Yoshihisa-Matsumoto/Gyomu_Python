from gyomu_infra.logger import logger
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.snapshot.analyze import analyze_project_changes
from gyomu_python_analysis.snapshot.models import FileDeleted
from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.schemas.types import FullPath
from gyomu_schema.utility.context import caller_context
from returns.result import Failure, Result, Success

from gyomu_workflow.snapshot.models import SnapshotTarget, SnapshotTargetOption
from gyomu_workflow.snapshot.validate import validate_python_package_structure


def resolve_snapshot_target(
    repository_root_path: FullPath,
    project_context: ProjectContext,
    option: SnapshotTargetOption,
) -> Result[SnapshotTarget, GyomuError]:
    """Resolve snapshot target files and current snapshot.

    Resolves the snapshot target files and current snapshot based on project changes and
    options.

    Args:
        repository_root_path (FullPath): Root path of the repository.
        project_context (ProjectContext): Project context information.
        option (SnapshotTargetOption): Options for snapshot target resolution.

    Returns:
        Result[SnapshotTarget, GyomuError]: A Result containing the resolved
            SnapshotTarget or a GyomuError.
    """
    validation_result = validate_python_package_structure(project_context)
    context = caller_context()

    if isinstance(validation_result, Failure):
        return validation_result.alt(
            lambda error: GyomuError(
                message="fail to validate project structure",
                domain="snapshot",
                operation="resolve_snapshot_target",
                reason="external_failure",
                context=context,
            ).chain(error)
        )

    result = analyze_project_changes(
        repository_root_path=repository_root_path,
        project_context=project_context,
        include_all=option.all,
    )
    if isinstance(result, Failure):
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
    logger.debug_object(change_result.diff)
    if option.file_filter is None:
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
    """Filter included files by a path pattern.

    Filters included files matching the given pattern path.

    Args:
        included_files (frozenset[ProjectRelativePath]): Set of included project
            relative files.
        path (str): Pattern string to match against.

    Returns:
        frozenset[ProjectRelativePath]: A frozenset of project relative paths matching
            the pattern.
    """
    return frozenset(
        (
            included_file
            for included_file in included_files
            if included_file.match(path)
        ),
    )
