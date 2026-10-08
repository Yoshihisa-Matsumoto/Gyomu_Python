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
    """Defines the steps in the workflow pipeline."""

    DOCSTRING = "docstring"

    DIRECTORY_CONCEPT = "directoryConcept"
    """Directory concept step."""

    PACKAGE_CONCEPT = "packageConcept"
    """Package concept step."""

    README = "README"
    """README step."""

    LLM_CONTEXT = "LLMContext"
    """LLM context step."""


class Checkpoint(BaseModel):
    """Represents a checkpoint holding the package name and completed workflow steps."""

    package: str
    """Package name associated with the checkpoint."""

    completed_steps: tuple[PipelineStep, ...]
    """Tuple of completed pipeline steps."""


@dataclass(frozen=True)
class SnapshotActionResult:
    """Holds the result of a snapshot action including its checkpoint and project
    snapshot.
    """

    checkpoint: Checkpoint
    """The updated checkpoint."""

    snapshot: ProjectSnapshot | None
    """The generated project snapshot."""


def _get_checkpoint_path(request: SnapshotRequest) -> FullPath:
    """Retrieves the file path for the checkpoint corresponding to the snapshot request.

    Args:
        request (SnapshotRequest):
    """
    project_id = to_project_id(request.project.path)
    return FullPath(Path(".gyomu") / "checkpoint" / project_id / "Checkpoint.json")


def _is_complete(checkpoint: Checkpoint) -> bool:
    """Checks whether the pipeline has completed the package concept step.

    Args:
        checkpoint (Checkpoint):
    """
    return PipelineStep.LLM_CONTEXT in checkpoint.completed_steps


def load_checkpoint(
    request: SnapshotRequest, diff: tuple[FileChange, ...]
) -> Checkpoint:
    """Loads an existing checkpoint or initializes a new one based on the request and
    file changes.

    Args:
        request (SnapshotRequest):
        diff (tuple[FileChange, ...]):
    """
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
    """Updates the checkpoint by adding a new completed step and saving it to disk.

    Args:
        checkpoint (Checkpoint):
        request (SnapshotRequest):
        status_to_add (PipelineStep):
    """

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
    """Initializes a new checkpoint with the given project name and no completed steps.

    Args:
        project_name (str):
    """
    return Checkpoint(package=project_name, completed_steps=tuple())
