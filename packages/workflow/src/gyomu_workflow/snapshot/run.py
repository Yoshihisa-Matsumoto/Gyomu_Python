from gyomu_infra.logger import logger
from gyomu_python_analysis.analysis.delete_cache import delete_module_cache
from gyomu_python_analysis.snapshot.analyze import analyze_project_changes
from gyomu_python_analysis.snapshot.commit import commit_project_changes
from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.option.update import UpdateDebugInfoOption, UpdateOption
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.schemas.snapshot.types import ProjectSnapshot
from gyomu_schema.utility.context import caller_context
from returns.result import Failure, Result, Success

from gyomu_workflow.snapshot.models import SnapshotRequest, SnapshotTarget
from gyomu_workflow.snapshot.normalize import normalize_filter
from gyomu_workflow.snapshot.run_docstring import run_docstring_action
from gyomu_workflow.snapshot.target import resolve_snapshot_target


async def run_snapshot(request: SnapshotRequest) -> Result[None, GyomuError]:
    """Run the snapshot workflow based on the provided request.

    Args:
        request (SnapshotRequest): The snapshot request configuration and context.

    Returns:
        Result[None, GyomuError]: A Result indicating success with None or failure with
            GyomuError.
    """
    normalize_filter(request.option.target)
    logger.debug(f"file_filter: {repr(request.option.target.file_filter)}")
    target_result = resolve_snapshot_target(
        repository_root_path=request.repository_root_path,
        project_context=request.project_context,
        option=request.option.target,
    )
    if isinstance(target_result, Failure):
        return target_result

    target = target_result.unwrap()

    logger.debug(repr(target.files))
    if len(target.files) == 0:
        logger.debug_object(target.snapshot.files)
    current_snapshot = target.snapshot

    action_result = await run_actions(request=request, target=target)

    if isinstance(action_result, Failure):
        return action_result
    current_snapshot = action_result.unwrap()

    if request.option.commit:
        commit_result = commit_project_changes(
            repository_root_path=request.repository_root_path,
            project_context=request.project_context,
            expected_snapshot=current_snapshot,
        )
        if isinstance(commit_result, Failure):
            context = caller_context()
            return commit_result.alt(
                lambda error: GyomuError(
                    message="fail to commit project changes",
                    domain="snapshot",
                    operation="run_snapshot",
                    reason="external_failure",
                    context=context,
                ).chain(error)
            )
    return Success(None)


async def run_actions(
    request: SnapshotRequest, target: SnapshotTarget
) -> Result[ProjectSnapshot, GyomuError]:
    """Execute requested actions on the snapshot target files.

    Args:
        request (SnapshotRequest): The snapshot request configuration.
        target (SnapshotTarget): The target snapshot data and file lists.

    Returns:
        Result[ProjectSnapshot, GyomuError]: A Result containing the updated
            ProjectSnapshot or a GyomuError.
    """
    current_snapshot = target.snapshot
    context = caller_context()
    option = build_docstring_update_option(request.option.action.docstring.log_keyword)
    # Do Action

    for deleted in target.deleted_files:
        if is_source_file(deleted, request.project_context.source_root):
            delete_result = delete_module_cache(
                request.project_context, file_path=deleted
            )
            if isinstance(delete_result, Failure):
                return delete_result.alt(
                    lambda error: GyomuError(
                        "fail to delete unnecessary module cache",
                        domain="snapshot",
                        operation="run_actions",
                        reason="external_failure",
                        context=context,
                    ).chain(error)
                )
    project_context = request.project_context

    for file in target.files:
        if is_source_file(file, request.project_context.source_root):
            if request.option.action.docstring.enabled:
                docstring_action_result = await run_docstring_action(
                    project_context=project_context,
                    source_project_relative_path=file,
                    option=option,
                )
                if isinstance(docstring_action_result, Failure):
                    return docstring_action_result
            if request.option.action.unit_test:
                pass

    # Post Action
    if (
        request.option.action.docstring.enabled
        or request.option.action.project_context
        or request.option.action.unit_test
    ):
        analysis_result = analyze_project_changes(
            repository_root_path=request.repository_root_path,
            project_context=request.project_context,
        )
        if isinstance(analysis_result, Failure):
            return analysis_result.alt(
                lambda error: GyomuError(
                    message="fail to analyze project change",
                    domain="snapshot",
                    operation="run_actions",
                    reason="external_failure",
                    context=context,
                ).chain(error)
            )
        current_snapshot = analysis_result.unwrap().current_snapshot

    return Success(current_snapshot)


def build_docstring_update_option(
    log_keyword: str | None,
) -> UpdateOption:
    """Construct the docstring update option configuration.

    Args:
        log_keyword (str | None): Optional keyword for logging.

    Returns:
        UpdateOption: The constructed UpdateOption configuration.
    """
    return UpdateOption(
        debug_info=UpdateDebugInfoOption(
            dump_to_file=True,
            updated_symbol_docstring=True,
            file_update_plan=True,
            rendered_symbol_docstring=True,
            docstring_update_plan=True,
            docstring_update_context=True,
            keyword=log_keyword,
        ),
        no_check_cache=True,
    )


def is_source_file(
    file_path: ProjectRelativePath, source_root: ProjectRelativePath
) -> bool:
    """Check whether a file path is a source file.

    Args:
        file_path (ProjectRelativePath): Path of the file to check.
        source_root (ProjectRelativePath): Root directory path of the source files.

    Returns:
        bool: True if the file is a source file, False otherwise.
    """
    return file_path.is_relative_to(source_root)
