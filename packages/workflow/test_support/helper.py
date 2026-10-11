from pathlib import Path

from gyomu_schema.schemas.python.types import ProjectRelativePath, WorkspaceRelativePath
from gyomu_schema.schemas.snapshot.types import ProjectSnapshot
from gyomu_workflow.snapshot.checkpoint import (
    Checkpoint,
    Fingerprints,
    InputFingerprint,
    PipelineStep,
)
from gyomu_workflow.snapshot.models import SnapshotTarget

from packages.python_analysis.python_analysis_test_support.helpers import (
    create_project_snapshot,
)


def create_input_fingerprint(
    paths: tuple[ProjectRelativePath, ...]
    | tuple[WorkspaceRelativePath, ...] = tuple(),
    hash: str = "ABC",
) -> InputFingerprint:
    return InputFingerprint(paths=paths, hash=hash)


def create_fingerprints(
    deleted_files: frozenset[ProjectRelativePath] = frozenset(),
    source_fingerprint: InputFingerprint = create_input_fingerprint(  # noqa: B008
        paths=(ProjectRelativePath(Path("src/a.py")),),  # noqa: B008
        hash="SOURCE_HASH***",  # noqa: B008
    ),  # noqa: B008
    project_fingerprint: InputFingerprint = create_input_fingerprint(  # noqa: B008
        paths=(ProjectRelativePath(Path("pyproject.toml")),),  # noqa: B008
        hash="PROJECT_HASH***",  # noqa: B008
    ),
    workspace_fingerprint: InputFingerprint = create_input_fingerprint(  # noqa: B008
        paths=(WorkspaceRelativePath(Path(".gyomu/knowledge/Package.yaml")),),  # noqa: B008
        hash="WORKSPACE_HASH***",  # noqa: B008
    ),  # noqa: B008
) -> Fingerprints:
    return Fingerprints(
        deleted_files=deleted_files,
        source_fingerprint=source_fingerprint,
        project_fingerprint=project_fingerprint,
        workspace_fingerprint=workspace_fingerprint,
    )


def create_snapshot_target(
    files: frozenset[ProjectRelativePath] = frozenset(),
    deleted_files: frozenset[ProjectRelativePath] = frozenset(),
    snapshot: ProjectSnapshot = create_project_snapshot(),  # noqa: B008
) -> SnapshotTarget:
    return SnapshotTarget(files=files, deleted_files=deleted_files, snapshot=snapshot)


def create_checkpoint(
    fingerprints: Fingerprints = create_fingerprints(),  # noqa: B008
    package: str = "test-package",
    completed_steps: tuple[PipelineStep, ...] = tuple(),
) -> Checkpoint:
    return Checkpoint(
        package=package,
        completed_steps=completed_steps,
        fingerprints=fingerprints,
    )
