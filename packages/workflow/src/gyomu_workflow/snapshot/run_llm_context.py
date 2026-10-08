from gyomu_concept.llm_context.definition import LLMCONTEXT_DOCUMENT_DEFINITION
from gyomu_concept.llm_context.generate import generate_llm_context_files
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.utility.context import caller_context
from returns.result import Failure, Result, Success

from gyomu_workflow.snapshot.checkpoint import (
    Checkpoint,
    PipelineStep,
    SnapshotActionResult,
    update_checkpoint,
)
from gyomu_workflow.snapshot.models import SnapshotRequest
from gyomu_workflow.snapshot.snapshot import update_snapshot


async def run_llm_context_action(
    current_checkpoint: Checkpoint,
    request: SnapshotRequest,
    option: ConceptOption,
) -> Result[SnapshotActionResult, GyomuError]:
    """Runs the LLM Context generation action for the snapshot pipeline.

    Returns:
        Result[SnapshotActionResult, GyomuError]: Result containing SnapshotActionResult
            on success or GyomuError on failure
    """
    context = caller_context()
    if (
        PipelineStep.LLM_CONTEXT not in current_checkpoint.completed_steps
        or not _are_llm_context_files_exist(request.project_context)
    ):
        llm_context_result = await generate_llm_context_files(
            project=request.project_context, option=option
        )
        if isinstance(llm_context_result, Failure):
            return llm_context_result.alt(
                lambda error: GyomuError(
                    message="fail to generate README.md file",
                    domain="snapshot",
                    operation="run_actions",
                    reason="external_failure",
                    context=context,
                ).chain(error)
            )

        snapshot_result = update_snapshot(request)
        if isinstance(snapshot_result, Failure):
            return snapshot_result

        return update_checkpoint(
            checkpoint=current_checkpoint,
            request=request,
            status_to_add=PipelineStep.LLM_CONTEXT,
        ).map(
            lambda checkpoint: SnapshotActionResult(
                checkpoint=checkpoint, snapshot=snapshot_result.unwrap()
            )
        )
    else:
        return Success(
            SnapshotActionResult(checkpoint=current_checkpoint, snapshot=None)
        )


def _are_llm_context_files_exist(project_context: ProjectContext) -> bool:
    """Checks if all required LLM Context  files exist for the project context.

    Returns:
        bool: True if all LLM Context  files exist, False otherwise
    """
    definition = LLMCONTEXT_DOCUMENT_DEFINITION

    for language in definition.supported_languages:
        output_file_path = definition.output.filepath_resolver.resolve(
            project_context, language
        )
        if not output_file_path.exists():
            return False

    return True
