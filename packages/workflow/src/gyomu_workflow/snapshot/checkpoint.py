from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum
from functools import partial
from pathlib import Path

from gyomu_infra.filesystem.file_io import read_json, write_json
from gyomu_infra.hash.hash import hash_file, hash_object
from gyomu_python_analysis.analysis.workspace import enumerate_workspace_target_files
from gyomu_python_analysis.snapshot.project import to_project_id
from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.error.io import GyomuIOError
from gyomu_schema.schemas.python.types import ProjectRelativePath, WorkspaceRelativePath
from gyomu_schema.schemas.snapshot.types import ProjectSnapshot
from gyomu_schema.schemas.types import FullPath
from gyomu_schema.utility.context import caller_context
from pydantic import BaseModel
from returns.result import Failure, Result, Success

from gyomu_workflow.snapshot.models import SnapshotRequest, SnapshotTarget


class PipelineStep(StrEnum):
    """Defines the steps in the workflow pipeline."""

    DOCSTRING = "docstring"
    """Docstring step."""

    DIRECTORY_CONCEPT = "directoryConcept"
    """Directory concept step."""

    PACKAGE_CONCEPT = "packageConcept"
    """Package concept step."""

    README = "README"
    """README step."""

    LLM_CONTEXT = "LLMContext"
    """LLM context step."""


class InputFingerprint(BaseModel):
    """Represents an input fingerprint with file paths and a hash."""

    paths: tuple[ProjectRelativePath, ...] | tuple[WorkspaceRelativePath, ...]
    """File paths included in the fingerprint."""

    hash: str
    """Hash representing the fingerprint contents."""


class Fingerprints(BaseModel):
    """Holds various fingerprints and deleted file records for input validation."""

    deleted_files: frozenset[ProjectRelativePath]
    """Set of deleted project relative files."""

    source_fingerprint: InputFingerprint
    """Fingerprint of source files."""

    project_fingerprint: InputFingerprint
    """Fingerprint of project non-source files."""

    workspace_fingerprint: InputFingerprint
    """Fingerprint of workspace target files."""


class Checkpoint(BaseModel):
    """Represents a checkpoint holding the package name and completed workflow steps."""

    package: str
    """Package name associated with the checkpoint."""

    completed_steps: tuple[PipelineStep, ...]
    """Tuple of completed pipeline steps."""

    fingerprints: Fingerprints
    """Fingerprints associated with the checkpoint."""


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


def _to_hash_error(
    err: GyomuIOError, path: WorkspaceRelativePath, caller: str
) -> GyomuError:
    """Converts a file IO error into a GyomuError for hashing operations."""

    return GyomuError(
        message=f"fail to hash file: {path}",
        domain="snapshot",
        operation="calculate workspace hash",
        reason="external_failure",
        context=caller,
    ).chain(err)


def _calculate_workspace_hash(
    workspace_path: FullPath,
    paths: tuple[WorkspaceRelativePath, ...],
) -> Result[str, GyomuError]:
    """Calculates a combined hash for workspace files."""

    files: list[tuple[Path, str]] = []
    caller = caller_context()
    for path in paths:
        file_full_path = workspace_path / path
        result = hash_file(file_full_path).alt(
            partial(_to_hash_error, path=path, caller=caller)
        )
        if isinstance(result, Failure):
            return result
        files.append((path, result.unwrap()))

    entries = sorted((str(path), raw_hash) for path, raw_hash in files)

    return Success(hash_object(entries))


def _get_workspace_fingerprint(
    request: SnapshotRequest,
) -> Result[InputFingerprint, GyomuError]:
    """Retrieves the input fingerprint for the workspace."""

    files = enumerate_workspace_target_files(request.workspace)
    hash_result = _calculate_workspace_hash(
        workspace_path=request.workspace.path, paths=files
    )
    if isinstance(hash_result, Failure):
        return hash_result

    return Success(InputFingerprint(paths=files, hash=hash_result.unwrap()))


def _create_input_fingerprint(
    files: Iterable[tuple[ProjectRelativePath, str]],
) -> InputFingerprint:
    """Creates an input fingerprint from a collection of file paths and hashes."""

    entries = tuple(sorted(files))

    return InputFingerprint(
        paths=tuple(path for path, _ in entries),
        hash=hash_object(tuple((str(path), raw_hash) for path, raw_hash in entries)),
    )


def _get_fingerprint(
    request: SnapshotRequest, target: SnapshotTarget
) -> Result[Fingerprints, GyomuError]:
    """Computes and retrieves fingerprints for the request and snapshot target."""

    snapshot = target.snapshot
    source_files = tuple(
        (file.project_relative_path, file.raw_hash)
        for file in snapshot.files
        if file.project_relative_path.is_relative_to(
            request.project_context.source_root
        )
    )

    project_files = tuple(
        (file.project_relative_path, file.raw_hash)
        for file in snapshot.files
        if not file.project_relative_path.is_relative_to(
            request.project_context.source_root
        )
    )

    source_fingerprint = _create_input_fingerprint(source_files)
    project_fingerprint = _create_input_fingerprint(project_files)

    workspace_fingerprint_result = _get_workspace_fingerprint(request)
    if isinstance(workspace_fingerprint_result, Failure):
        return workspace_fingerprint_result
    workspace_fingerprint = workspace_fingerprint_result.unwrap()

    return Success(
        Fingerprints(
            deleted_files=target.deleted_files,
            source_fingerprint=source_fingerprint,
            project_fingerprint=project_fingerprint,
            workspace_fingerprint=workspace_fingerprint,
        )
    )


def load_checkpoint(
    request: SnapshotRequest, target: SnapshotTarget
) -> Result[Checkpoint, GyomuError]:
    """Loads an existing checkpoint or initializes a new one based on the request and
    file changes.

    Args:
        request (SnapshotRequest):
        diff (tuple[FileChange, ...]):
    """
    checkfile_path = _get_checkpoint_path(request)

    fingerprints_result = _get_fingerprint(request=request, target=target)
    if isinstance(fingerprints_result, Failure):
        return fingerprints_result
    fingerprints = fingerprints_result.unwrap()

    if checkfile_path.exists():
        load_result = read_json(path=checkfile_path, model_type=Checkpoint)
        if isinstance(load_result, Success):
            checkpoint = load_result.unwrap()
            _update_fingerprints(checkpoint, fingerprints=fingerprints)
            return Success(checkpoint)

    return Success(
        Checkpoint(
            package=request.project_context.config.name,
            completed_steps=tuple(),
            fingerprints=fingerprints,
        )
    )


def _is_files_same(
    source: frozenset[ProjectRelativePath], target: frozenset[ProjectRelativePath]
) -> bool:
    """Checks if two sets of project relative files are identical."""

    if len(source) != len(target):
        return False
    for file in source:
        if file not in target:
            return False

    return all(file in source for file in target)


def _is_fingerprint_same(source: InputFingerprint, target: InputFingerprint) -> bool:
    """Checks if two input fingerprints are identical."""

    if source.hash != target.hash:
        return False

    for file_path in source.paths:
        if file_path not in target.paths:
            return False

    return all(file_path in source.paths for file_path in target.paths)


def _unset_status(
    checkpoint: Checkpoint,
    unset_targets: tuple[PipelineStep, ...],
) -> None:
    """Unsets specified pipeline steps from the checkpoint."""

    completed_steps = tuple(
        status for status in checkpoint.completed_steps if status not in unset_targets
    )
    checkpoint.completed_steps = completed_steps
    return


def _update_fingerprints(checkpoint: Checkpoint, fingerprints: Fingerprints) -> None:
    """Updates checkpoint fingerprints and resets completed steps if changes are
    detected.
    """
    if not _is_files_same(
        checkpoint.fingerprints.deleted_files, fingerprints.deleted_files
    ):
        checkpoint.fingerprints = fingerprints
        checkpoint.completed_steps = tuple()
        return

    if not _is_fingerprint_same(
        checkpoint.fingerprints.source_fingerprint, fingerprints.source_fingerprint
    ):
        checkpoint.fingerprints = fingerprints
        checkpoint.completed_steps = tuple()
        return

    if not _is_fingerprint_same(
        checkpoint.fingerprints.project_fingerprint, fingerprints.project_fingerprint
    ):
        checkpoint.fingerprints = fingerprints
        _unset_status(checkpoint, (PipelineStep.README, PipelineStep.LLM_CONTEXT))
        return

    if not _is_fingerprint_same(
        checkpoint.fingerprints.workspace_fingerprint,
        fingerprints.workspace_fingerprint,
    ):
        checkpoint.fingerprints = fingerprints
        _unset_status(checkpoint=checkpoint, unset_targets=(PipelineStep.LLM_CONTEXT,))


def update_checkpoint(
    checkpoint: Checkpoint,
    request: SnapshotRequest,
    status_to_add: PipelineStep,
    target: SnapshotTarget,
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

    fingerprints_result = _get_fingerprint(request=request, target=target)
    if isinstance(fingerprints_result, Failure):
        return fingerprints_result
    fingerprints = fingerprints_result.unwrap()

    new_checkpoint = Checkpoint(
        completed_steps=tuple(current_steps),
        package=checkpoint.package,
        fingerprints=fingerprints,
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
