from gyomu_concept.package.concept import build_package_concept
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


async def run_package_action(
    current_checkpoint: Checkpoint,
    request: SnapshotRequest,
    option: ConceptOption,
) -> Result[SnapshotActionResult, GyomuError]:
    context = caller_context()
    package_result = await build_package_concept(
        context=request.project_context, option=option
    )
    if isinstance(package_result, Failure):
        return package_result.alt(
            lambda error: GyomuError(
                message="fail to generate package concept",
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
        status_to_add=PipelineStep.PACKAGE_CONCEPT,
    ).map(
        lambda checkpoint: SnapshotActionResult(
            checkpoint=checkpoint, snapshot=snapshot_result.unwrap()
        )
    )
