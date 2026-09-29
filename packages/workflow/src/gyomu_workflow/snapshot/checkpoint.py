from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from gyomu_infra.filesystem.file_io import read_json, write_json
from gyomu_python_analysis.snapshot.project import to_project_id
from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.schemas.snapshot.types import FileChange, ProjectSnapshot
from gyomu_schema.schemas.types import FullPath
from gyomu_schema.utility.context import caller_context
from pydantic import BaseModel
from returns.result import Result, Success

from gyomu_workflow.snapshot.models import SnapshotRequest


class PipelineStep(StrEnum):
    DIRECTORY_CONCEPT = "directoryConcept"
    PACKAGE_CONCEPT = "packageConcept"
    README = "README"
    LLM_CONTEXT = "LLMContext"


class Checkpoint(BaseModel):
    package: str

    completed_steps: tuple[PipelineStep, ...]


@dataclass(frozen=True)
class SnapshotActionResult:
    checkpoint: Checkpoint
    snapshot: ProjectSnapshot


def _get_checkpoint_path(request: SnapshotRequest) -> FullPath:
    project_id = to_project_id(request.project.path)
    return FullPath(Path(".gyomu") / "checkpoint" / project_id / "Checkpoint.json")


def _is_complete(checkpoint: Checkpoint) -> bool:
    return PipelineStep.PACKAGE_CONCEPT in checkpoint.completed_steps


def load_checkpoint(
    request: SnapshotRequest, diff: tuple[FileChange, ...]
) -> Checkpoint:
    checkfile_path = _get_checkpoint_path(request)

    if checkfile_path.exists():
        load_result = read_json(path=checkfile_path, model_type=Checkpoint)
        if isinstance(load_result, Success):
            checkpoint: Checkpoint = load_result.unwrap()
            if not _is_complete(checkpoint):
                return checkpoint
            if len(diff) == 0:
                return checkpoint

    return initialize_checkpoint(request.project_context.config.name)


def update_checkpoint(
    checkpoint: Checkpoint, request: SnapshotRequest, status_to_add: PipelineStep
) -> Result[Checkpoint, GyomuError]:

    checkfile_path = _get_checkpoint_path(request)
    current_steps: list[PipelineStep] = [item for item in checkpoint.completed_steps]
    if status_to_add not in current_steps:
        current_steps.append(status_to_add)

    new_checkpoint = Checkpoint(
        completed_steps=tuple(current_steps),
        package=checkpoint.package,
    )
    return (
        write_json(path=checkfile_path, value=new_checkpoint, value_type=Checkpoint)
        .alt(
            lambda error: GyomuError(
                message="fail to update checkpoint",
                domain="snapshot",
                operation="update_checkpoint",
                reason="external_failure",
                context=caller_context(),
            ).chain(error)
        )
        .map(lambda _: new_checkpoint)
    )


def initialize_checkpoint(project_name: str) -> Checkpoint:
    return Checkpoint(package=project_name, completed_steps=tuple())
