from pathlib import Path

from gyomu_schema.schemas.python.types import ProjectRelativePath, WorkspaceRelativePath
from gyomu_schema.schemas.snapshot.types import ProjectSnapshot
from gyomu_workflow.snapshot.checkpoint import (
    Checkpoint,
    Fingerprints,
    InputFingerprint,
    PipelineStep,
)
from gyomu_workflow.snapshot.error import (
    PyProjectStructureErrorKind,
    PyProjectStructureValidationError,
    PyProjectStructureValidationErrors,
)
from gyomu_workflow.snapshot.models import (
    DocstringExecutionOption,
    FileFilter,
    SnapshotActionOption,
    SnapshotExecutionOption,
    SnapshotTarget,
    SnapshotTargetOption,
)

from packages.python_analysis.python_analysis_test_support.helpers import (
    create_project_snapshot,
)


def create_snapshot_target_option(
    all: bool = False, file_filter: FileFilter | None = None
) -> SnapshotTargetOption:
    return SnapshotTargetOption(all=all, file_filter=file_filter)


def create_docstring_execution_ption(
    enabled: bool = True, log_keyword: str | None = None
) -> DocstringExecutionOption:
    return DocstringExecutionOption(enabled=enabled, log_keyword=log_keyword)


def create_snapshot_action_option(
    docstring: DocstringExecutionOption = create_docstring_execution_ption(),  # noqa: B008
    project_context: bool = False,
    unit_test: bool = False,
) -> SnapshotActionOption:
    return SnapshotActionOption(
        docstring=docstring, project_context=project_context, unit_test=unit_test
    )


def create_snapshot_execution_option(
    commit: bool = True,
    target: SnapshotTargetOption = create_snapshot_target_option(),  # noqa: B008
    action: SnapshotActionOption = create_snapshot_action_option(),  # noqa: B008
) -> SnapshotExecutionOption:
    return SnapshotExecutionOption(commit=commit, target=target, action=action)


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


def create_py_project_structure_validation_error(
    kind: PyProjectStructureErrorKind = PyProjectStructureErrorKind.MISSING_INIT_FILE,
    path: ProjectRelativePath = ProjectRelativePath(Path("src/foo")),  # noqa: B008
    message: str = "test",
) -> PyProjectStructureValidationError:
    return PyProjectStructureValidationError(message=message, path=path, kind=kind)


def create_py_project_structure_validation_errors(
    errors: tuple[PyProjectStructureValidationError, ...] = (
        create_py_project_structure_validation_error(),
    ),
    message: str = "Invalid structure on project",
    project_name: str = "test-project",
) -> PyProjectStructureValidationErrors:
    return PyProjectStructureValidationErrors(
        message=message,
        project_name=project_name,
        errors=errors,
    )
