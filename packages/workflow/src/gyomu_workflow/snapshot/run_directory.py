from gyomu_concept.directory.build import build_directory_concept
from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.utility.context import caller_context
from returns.result import Failure, Result

from gyomu_workflow.snapshot.checkpoint import (
    Checkpoint,
    PipelineStep,
    SnapshotActionResult,
    update_checkpoint,
)
from gyomu_workflow.snapshot.models import SnapshotRequest
from gyomu_workflow.snapshot.snapshot import update_snapshot


async def run_directory_action(
    current_checkpoint: Checkpoint,
    request: SnapshotRequest,
    option: ConceptOption,
) -> Result[SnapshotActionResult, GyomuError]:
    """Executes the directory generation and snapshot update action.

    Args:
        current_checkpoint (Checkpoint): The current execution checkpoint.
        request (SnapshotRequest): The snapshot request containing project context and
            options.
        option (ConceptOption): The concept option for directory generation.

    Returns:
        Result[SnapshotActionResult, GyomuError]: A Result containing either the
            SnapshotActionResult on success or a GyomuError on failure.
    """
    context = caller_context()
    directory_result = await build_directory_concept(
        context=request.project_context, option=option
    )
    if isinstance(directory_result, Failure):
        return directory_result.alt(
            lambda error: GyomuError(
                message="fail to generate directory concept",
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
        status_to_add=PipelineStep.DIRECTORY_CONCEPT,
    ).map(
        lambda checkpoint: SnapshotActionResult(
            checkpoint=checkpoint, snapshot=snapshot_result.unwrap()
        )
    )
