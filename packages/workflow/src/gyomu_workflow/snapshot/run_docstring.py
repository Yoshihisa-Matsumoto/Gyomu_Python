from pathlib import Path

from gyomu_docstring.update.process import process_docstring_update
from gyomu_infra.logger import logger
from gyomu_python_analysis.analysis.delete_cache import delete_module_cache
from gyomu_python_analysis.analysis.load_file_context import load_file_analysis_context
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.snapshot.analyze import analyze_project_changes
from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.option.update import UpdateDebugInfoOption, UpdateOption
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.utility.context import caller_context
from returns.result import Failure, Result, Success

from gyomu_workflow.snapshot.checkpoint import (
    Checkpoint,
    PipelineStep,
    SnapshotActionResult,
    update_checkpoint,
)
from gyomu_workflow.snapshot.models import SnapshotRequest, SnapshotTarget


def is_source_docstring_target(
    project_context: ProjectContext,
    source_project_relative_path: ProjectRelativePath,
) -> bool:
    """Determine if a source path is a target for docstring processing.

    Determines whether a source file is a target for docstring generation based on
    project exclusion configurations.

    Args:
        project_context (ProjectContext): The project context containing configuration
            settings.
        source_project_relative_path (ProjectRelativePath): The relative path of the
            source file within the project.

    Returns:
        bool: True if the source file is a docstring target, otherwise False.
    """
    exclude_path_list = project_context.config.get_attribute(
        "tool.gyomu.exclude", list[str]
    )
    if exclude_path_list is None:
        return True
    return not any(
        source_project_relative_path.is_relative_to(Path(exclude_path))
        for exclude_path in exclude_path_list
    )


async def run_docstring_action(
    project_context: ProjectContext,
    source_project_relative_path: ProjectRelativePath,
    option: UpdateOption,
) -> Result[None, GyomuError]:
    """Run the docstring update action for a specified source file.

    Executes the docstring update action for a given source file within the project.

    Args:
        project_context (ProjectContext): The project context containing configuration
            and analysis settings.
        source_project_relative_path (ProjectRelativePath): The relative path of the
            source file to process.
        option (UpdateOption): The update options controlling analysis and modification
            behavior.

    Returns:
        Result[None, GyomuError]: A Result indicating success with None or a GyomuError
            on failure.
    """
    if not is_source_docstring_target(project_context, source_project_relative_path):
        logger.info(f"Not Scope of Docstring:{source_project_relative_path}")
        return Success(None)

    file_path = source_project_relative_path
    context = caller_context()

    file_analysis_result = load_file_analysis_context(
        context=project_context, file_path=file_path, option=option
    )
    if isinstance(file_analysis_result, Failure):
        return file_analysis_result.alt(
            lambda error: GyomuError(
                "fail to analyze source file",
                domain="snapshot",
                operation="run_docstring_action",
                reason="external_failure",
                context=context,
                details={"file_path": file_path},
            ).chain(error)
        )

    file_context = file_analysis_result.unwrap()
    docstring_update_result = await process_docstring_update(
        context=project_context, file_context=file_context, option=option
    )
    if isinstance(docstring_update_result, Failure):
        return docstring_update_result.alt(
            lambda error: GyomuError(
                "fail to update docstring",
                domain="snapshot",
                operation="run_docstring_action",
                reason="external_failure",
                context=context,
                details={"file_path": file_path},
            ).chain(error)
        )
    return Success(None)


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


async def run_docstring_actions(
    current_checkpoint: Checkpoint,
    request: SnapshotRequest,
    target: SnapshotTarget,
) -> Result[SnapshotActionResult, GyomuError]:
    """Run docstring actions for snapshot workflow.

    Executes docstring actions for project files as part of the snapshot workflow.

    Args:
        current_checkpoint (Checkpoint): The current pipeline checkpoint.
        request (SnapshotRequest): The snapshot request containing configuration and
            action options.
        target (SnapshotTarget): The snapshot target specifying files and changes to
            process.

    Returns:
        Result[SnapshotActionResult, GyomuError]: A Result containing the updated
            SnapshotActionResult on success or a GyomuError on failure.
    """
    context = caller_context()
    option = build_docstring_update_option(request.option.action.docstring.log_keyword)
    if PipelineStep.DOCSTRING not in current_checkpoint.completed_steps:
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
        analysis = analysis_result.unwrap()
        current_snapshot = analysis.current_snapshot
        return update_checkpoint(
            checkpoint=current_checkpoint,
            request=request,
            status_to_add=PipelineStep.DOCSTRING,
            target=target,
        ).map(
            lambda checkpoint: SnapshotActionResult(
                checkpoint=checkpoint, snapshot=current_snapshot
            )
        )
    else:
        return Success(
            SnapshotActionResult(checkpoint=current_checkpoint, snapshot=None)
        )
