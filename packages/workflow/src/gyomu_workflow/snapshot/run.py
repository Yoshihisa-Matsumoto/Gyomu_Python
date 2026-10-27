from gyomu_infra.logger import logger
from gyomu_python_analysis.snapshot.commit import commit_project_changes
from gyomu_python_analysis.snapshot.models import AnalyzeProjectChangesResult
from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.option.concept import (
    ConceptActionOption,
    ConceptDebugInfoOption,
    ConceptOption,
)
from gyomu_schema.schemas.snapshot.types import FileChange, ProjectSnapshot
from gyomu_schema.utility.fromatting import format_object
from returns.result import Failure, Result, Success

from gyomu_workflow.snapshot.checkpoint import (
    load_checkpoint,
)
from gyomu_workflow.snapshot.models import SnapshotRequest, SnapshotTarget
from gyomu_workflow.snapshot.normalize import normalize_filter
from gyomu_workflow.snapshot.run_directory import run_directory_action
from gyomu_workflow.snapshot.run_docstring import run_docstring_actions
from gyomu_workflow.snapshot.run_llm_context import run_llm_context_action
from gyomu_workflow.snapshot.run_package import run_package_action
from gyomu_workflow.snapshot.run_readme import run_readme_action
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

    target, analysis = target_result.unwrap()

    logger.debug(repr(target.files))
    # if len(target.files) == 0:
    #     logger.debug_object(target.snapshot.files)
    current_snapshot = target.snapshot

    action_result = await run_actions(request=request, target=target, analysis=analysis)

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
            return commit_result.alt(
                lambda error: GyomuError(
                    message="fail to commit project changes",
                    domain="snapshot",
                    operation="run_snapshot",
                    reason="external_failure",
                ).chain(error)
            )
    return Success(None)


async def run_actions(
    request: SnapshotRequest,
    target: SnapshotTarget,
    analysis: AnalyzeProjectChangesResult,
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

    # Do Action

    checkpoint_result = load_checkpoint(request=request, target=target)
    if isinstance(checkpoint_result, Failure):
        return checkpoint_result
    current_checkpoint = checkpoint_result.unwrap()

    docstring_result = await run_docstring_actions(
        request=request,
        current_checkpoint=current_checkpoint,
        target=target,
    )
    if isinstance(docstring_result, Failure):
        return docstring_result
    action_result = docstring_result.unwrap()
    current_checkpoint = action_result.checkpoint
    if action_result.snapshot is not None:
        current_snapshot = action_result.snapshot

    # Post Action
    if (
        request.option.action.docstring.enabled
        or request.option.action.project_context
        or request.option.action.unit_test
    ):
        current_snapshot = analysis.current_snapshot
        logger.debug_object(analysis.diff)
        concept_option = build_concept_update_option(
            diff=analysis.diff,
            log_keyword=request.option.action.docstring.log_keyword,
        )

        # current_checkpoint = load_checkpoint(
        #     request=request,
        #     diff=analysis.diff,
        # )
        logger.debug(
            f"Checkpoint Status: {format_object(current_checkpoint.completed_steps)}"
        )
        if request.option.action.project_context:
            directory_result = await run_directory_action(
                request=request,
                current_checkpoint=current_checkpoint,
                option=concept_option,
                target=target,
            )
            if isinstance(directory_result, Failure):
                return directory_result
            action_result = directory_result.unwrap()
            current_checkpoint = action_result.checkpoint
            if action_result.snapshot is not None:
                current_snapshot = action_result.snapshot

            package_result = await run_package_action(
                request=request,
                current_checkpoint=current_checkpoint,
                option=concept_option,
                target=target,
            )
            if isinstance(package_result, Failure):
                return package_result
            action_result = package_result.unwrap()
            current_checkpoint = action_result.checkpoint
            if action_result.snapshot is not None:
                current_snapshot = action_result.snapshot

            readme_result = await run_readme_action(
                request=request,
                current_checkpoint=current_checkpoint,
                option=concept_option,
                target=target,
            )
            if isinstance(readme_result, Failure):
                return readme_result
            action_result = readme_result.unwrap()
            current_checkpoint = action_result.checkpoint
            if action_result.snapshot is not None:
                current_snapshot = action_result.snapshot

            llm_context_result = await run_llm_context_action(
                request=request,
                current_checkpoint=current_checkpoint,
                option=concept_option,
                target=target,
            )
            if isinstance(llm_context_result, Failure):
                return llm_context_result
            action_result = llm_context_result.unwrap()
            current_checkpoint = action_result.checkpoint
            if action_result.snapshot is not None:
                current_snapshot = action_result.snapshot

    return Success(current_snapshot)


def build_concept_update_option(
    diff: tuple[FileChange, ...],
    log_keyword: str | None,
) -> ConceptOption:
    """Construct the concept update option configuration.

    Args:
        diff (tuple[FileChange, ...]): Tuple of file changes.
        log_keyword (str | None): Optional keyword for logging.

    Returns:
        ConceptOption: The constructed ConceptOption configuration.
    """
    return ConceptOption(
        debug_info=ConceptDebugInfoOption(
            dump_to_file=True,
            keyword=log_keyword,
            directory_concept=True,
            package_concept=True,
            package_analysis=True,
            readme_sections=True,
        ),
        changed_files=diff,
        action=ConceptActionOption(),
    )
