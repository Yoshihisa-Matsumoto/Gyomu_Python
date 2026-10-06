from gyomu_concept.readme.definition import README_DOCUMENT_DEFINITION
from gyomu_concept.readme.generate import generate_readme_files
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


async def run_readme_action(
    current_checkpoint: Checkpoint,
    request: SnapshotRequest,
    option: ConceptOption,
) -> Result[SnapshotActionResult, GyomuError]:
    context = caller_context()
    if (
        PipelineStep.README not in current_checkpoint.completed_steps
        or not _are_readme_files_exist(request.project_context)
    ):
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
    else:
        return Success(
            SnapshotActionResult(checkpoint=current_checkpoint, snapshot=None)
        )


def _are_readme_files_exist(project_context: ProjectContext) -> bool:
    definition = README_DOCUMENT_DEFINITION

    for language in definition.supported_languages:
        output_file_path = definition.output.filepath_resolver.resolve(
            project_context, language
        )
        if not output_file_path.exists():
            return False

    return True
