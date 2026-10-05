from gyomu_concept.readme.generate import generate_readme_files
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


async def run_readme_action(
    current_checkpoint: Checkpoint,
    request: SnapshotRequest,
    option: ConceptOption,
) -> Result[SnapshotActionResult, GyomuError]:
    context = caller_context()
    readme_result = await generate_readme_files(
        project=request.project_context, option=option
    )
    if isinstance(readme_result, Failure):
        return readme_result.alt(
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
        status_to_add=PipelineStep.README,
    ).map(
        lambda checkpoint: SnapshotActionResult(
            checkpoint=checkpoint, snapshot=snapshot_result.unwrap()
        )
    )
