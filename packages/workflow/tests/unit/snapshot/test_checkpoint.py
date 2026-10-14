from pathlib import Path
from unittest.mock import ANY

from gyomu_infra.hash.hash import hash_object
from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.error.io import GyomuIOError, IOLayer, IOOperation
from gyomu_schema.schemas.python.types import (
    ProjectRelativePath,
    WorkspaceRelativePath,
)
from gyomu_schema.schemas.types import FullPath
from gyomu_workflow.snapshot.checkpoint import (
    Checkpoint,
    InputFingerprint,
    PipelineStep,
    _calculate_workspace_hash,
    _get_fingerprint,
    _get_workspace_fingerprint,
    _is_files_same,
    _is_fingerprint_same,
    _to_hash_error,
    _update_fingerprints,
    load_checkpoint,
    update_checkpoint,
)
from returns.result import Failure, Success

from packages.python_analysis.test_support.helpers import (
    create_file_snapshot,
    create_project_snapshot,
)
from packages.workflow.test_support.helper import (
    create_checkpoint,
    create_fingerprints,
    create_input_fingerprint,
    create_snapshot_target,
)


class TestIsFilesSame:
    def test_returns_true_for_same_files(self) -> None:
        files = frozenset(
            {
                ProjectRelativePath(Path("src/a.py")),
                ProjectRelativePath(Path("src/b.py")),
            }
        )

        assert _is_files_same(files, files) is True

    def test_returns_true_when_order_differs(self) -> None:
        source = frozenset(
            {
                ProjectRelativePath(Path("src/a.py")),
                ProjectRelativePath(Path("src/b.py")),
            }
        )
        target = frozenset(
            {
                ProjectRelativePath(Path("src/b.py")),
                ProjectRelativePath(Path("src/a.py")),
            }
        )

        assert _is_files_same(source, target) is True

    def test_returns_false_when_file_is_added(self) -> None:
        source = frozenset({ProjectRelativePath(Path("src/a.py"))})
        target = frozenset(
            {
                ProjectRelativePath(Path("src/a.py")),
                ProjectRelativePath(Path("src/b.py")),
            }
        )

        assert _is_files_same(source, target) is False

    def test_returns_false_when_file_is_removed(self) -> None:
        source = frozenset(
            {
                ProjectRelativePath(Path("src/a.py")),
                ProjectRelativePath(Path("src/b.py")),
            }
        )
        target = frozenset({ProjectRelativePath(Path("src/a.py"))})

        assert _is_files_same(source, target) is False

    def test_returns_true_for_empty_sets(self) -> None:
        assert _is_files_same(frozenset(), frozenset()) is True


class TestIsFingerprintSame:
    def test_returns_true_for_same_fingerprint(self) -> None:
        fingerprint = InputFingerprint(
            paths=(ProjectRelativePath(Path("src/a.py")),),
            hash="abc123",
        )

        assert _is_fingerprint_same(fingerprint, fingerprint) is True

    def test_returns_false_when_hash_differs(self) -> None:
        source = InputFingerprint(
            paths=(ProjectRelativePath(Path("src/a.py")),),
            hash="abc123",
        )
        target = InputFingerprint(
            paths=(ProjectRelativePath(Path("src/a.py")),),
            hash="def456",
        )

        assert _is_fingerprint_same(source, target) is False

    def test_returns_false_when_paths_differ(self) -> None:
        source = InputFingerprint(
            paths=(ProjectRelativePath(Path("src/a.py")),),
            hash="abc123",
        )
        target = InputFingerprint(
            paths=(ProjectRelativePath(Path("src/b.py")),),
            hash="abc123",
        )

        assert _is_fingerprint_same(source, target) is False

    def test_returns_false_when_path_is_added(self) -> None:
        source = InputFingerprint(
            paths=(ProjectRelativePath(Path("src/a.py")),),
            hash="abc123",
        )
        target = InputFingerprint(
            paths=(
                ProjectRelativePath(Path("src/a.py")),
                ProjectRelativePath(Path("src/b.py")),
            ),
            hash="abc123",
        )

        assert _is_fingerprint_same(source, target) is False

    def test_returns_true_for_empty_fingerprints(self) -> None:
        source = InputFingerprint(paths=(), hash="empty")
        target = InputFingerprint(paths=(), hash="empty")

        assert _is_fingerprint_same(source, target) is True


class TestUpdateFingerprints:
    def test_preserves_completed_steps_when_fingerprints_are_same(self) -> None:
        fingerprints = create_fingerprints()
        checkpoint = create_checkpoint(fingerprints)

        _update_fingerprints(checkpoint, fingerprints)

        assert checkpoint.completed_steps == tuple()

    def test_clears_all_steps_when_source_fingerprint_changes(self) -> None:
        checkpoint = create_checkpoint(create_fingerprints())
        updated = create_fingerprints()

        _update_fingerprints(checkpoint, updated)

        assert checkpoint.completed_steps == ()
        assert checkpoint.fingerprints == updated

    def test_clears_all_steps_when_deleted_files_change(self) -> None:
        checkpoint = create_checkpoint(create_fingerprints())
        updated = create_fingerprints(
            deleted_files=frozenset({ProjectRelativePath(Path("src/deleted.py"))})
        )

        _update_fingerprints(checkpoint, updated)

        assert checkpoint.completed_steps == ()
        assert checkpoint.fingerprints == updated

    def test_clears_readme_and_llm_context_when_project_changes(self) -> None:
        checkpoint = create_checkpoint(
            fingerprints=create_fingerprints(), completed_steps=tuple(PipelineStep)
        )
        updated = create_fingerprints(
            project_fingerprint=create_input_fingerprint(hash="changed")
        )

        _update_fingerprints(checkpoint, updated)

        assert checkpoint.completed_steps == (
            PipelineStep.DOCSTRING,
            PipelineStep.DIRECTORY_CONCEPT,
            PipelineStep.PACKAGE_CONCEPT,
        )
        assert checkpoint.fingerprints == updated

    def test_clears_only_llm_context_when_workspace_changes(self) -> None:
        checkpoint = create_checkpoint(completed_steps=tuple(PipelineStep))
        updated = create_fingerprints(
            workspace_fingerprint=create_input_fingerprint(hash="changed")
        )

        _update_fingerprints(checkpoint, updated)

        assert checkpoint.completed_steps == (
            PipelineStep.DOCSTRING,
            PipelineStep.DIRECTORY_CONCEPT,
            PipelineStep.PACKAGE_CONCEPT,
            PipelineStep.README,
        )
        assert checkpoint.fingerprints == updated


class TestGetFingerprint:
    def test_creates_fingerprints_from_all_snapshot_files(
        self, snapshot_request, mocker
    ) -> None:
        snapshot = create_project_snapshot(
            files=(
                create_file_snapshot(
                    ProjectRelativePath(Path("src/a.py")),
                    raw_hash="SOURCE_A_HASH",
                ),
                create_file_snapshot(
                    ProjectRelativePath(Path("src/b.py")),
                    raw_hash="SOURCE_B_HASH",
                ),
                create_file_snapshot(
                    ProjectRelativePath(Path("pyproject.toml")),
                    raw_hash="PROJECT_HASH",
                ),
            )
        )
        deleted_files = frozenset({ProjectRelativePath(Path("src/deleted.py"))})
        target = create_snapshot_target(
            files=frozenset({ProjectRelativePath(Path("src/a.py"))}),
            deleted_files=deleted_files,
            snapshot=snapshot,
        )
        workspace_fingerprint = create_input_fingerprint(
            paths=(WorkspaceRelativePath(Path(".gyomu/knowledge/Package.yaml")),),
            hash="WORKSPACE_HASH",
        )
        mocker.patch(
            "gyomu_workflow.snapshot.checkpoint._get_workspace_fingerprint",
            return_value=Success(workspace_fingerprint),
        )

        result = _get_fingerprint(snapshot_request, target)

        assert isinstance(result, Success)
        fingerprints = result.unwrap()

        assert fingerprints.source_fingerprint.paths == (
            ProjectRelativePath(Path("src/a.py")),
            ProjectRelativePath(Path("src/b.py")),
        )
        assert fingerprints.project_fingerprint.paths == (
            ProjectRelativePath(Path("pyproject.toml")),
        )
        assert fingerprints.source_fingerprint.hash
        assert fingerprints.project_fingerprint.hash
        assert fingerprints.deleted_files == deleted_files
        assert fingerprints.workspace_fingerprint == workspace_fingerprint

    def test_returns_failure_when_workspace_fingerprint_fails(
        self, snapshot_request, mocker
    ) -> None:
        target = create_snapshot_target()
        error = GyomuError(
            message="failed to calculate workspace fingerprint",
            domain="snapshot",
            operation="test",
            reason="external_failure",
            context="test",
        )
        mocker.patch(
            "gyomu_workflow.snapshot.checkpoint._get_workspace_fingerprint",
            return_value=Failure(error),
        )

        result = _get_fingerprint(snapshot_request, target)

        assert isinstance(result, Failure)
        assert result.failure() is error


class TestLoadCheckpoint:
    def test_initializes_checkpoint_when_file_does_not_exist(
        self, snapshot_request, mocker
    ) -> None:
        fingerprints = create_fingerprints()
        mocker.patch(
            "gyomu_workflow.snapshot.checkpoint._get_fingerprint",
            return_value=Success(fingerprints),
        )
        mocker.patch(
            "gyomu_workflow.snapshot.checkpoint._get_checkpoint_path",
            return_value=Path("nonexistent/Checkpoint.json"),
        )

        result = load_checkpoint(
            request=snapshot_request,
            target=create_snapshot_target(),
        )

        assert isinstance(result, Success)
        checkpoint = result.unwrap()
        assert checkpoint.package == snapshot_request.project_context.config.name
        assert checkpoint.completed_steps == tuple()
        assert checkpoint.fingerprints == fingerprints

    def test_loads_existing_checkpoint(self, snapshot_request, mocker) -> None:
        fingerprints = create_fingerprints()
        checkpoint = create_checkpoint(
            fingerprints=fingerprints,
            completed_steps=(
                PipelineStep.DOCSTRING,
                PipelineStep.DIRECTORY_CONCEPT,
            ),
        )
        checkpoint_path = Path("Checkpoint.json")
        mocker.patch(
            "gyomu_workflow.snapshot.checkpoint._get_fingerprint",
            return_value=Success(fingerprints),
        )
        mocker.patch(
            "gyomu_workflow.snapshot.checkpoint._get_checkpoint_path",
            return_value=checkpoint_path,
        )
        mocker.patch.object(Path, "exists", return_value=True)
        mocker.patch(
            "gyomu_workflow.snapshot.checkpoint.read_json",
            return_value=Success(checkpoint),
        )
        update_fingerprints = mocker.patch(
            "gyomu_workflow.snapshot.checkpoint._update_fingerprints"
        )

        result = load_checkpoint(
            request=snapshot_request,
            target=create_snapshot_target(),
        )

        assert isinstance(result, Success)
        assert result.unwrap() is checkpoint
        assert checkpoint.completed_steps == (
            PipelineStep.DOCSTRING,
            PipelineStep.DIRECTORY_CONCEPT,
        )
        update_fingerprints.assert_called_once_with(
            checkpoint, fingerprints=fingerprints
        )

    def test_updates_existing_checkpoint_when_fingerprints_change(
        self, snapshot_request, mocker
    ) -> None:
        old_fingerprints = create_fingerprints()
        new_fingerprints = create_fingerprints(
            source_fingerprint=create_input_fingerprint(
                paths=(ProjectRelativePath(Path("src/a.py")),),
                hash="CHANGED_SOURCE_HASH",
            )
        )
        checkpoint = create_checkpoint(
            fingerprints=old_fingerprints,
            completed_steps=tuple(PipelineStep),
        )
        mocker.patch(
            "gyomu_workflow.snapshot.checkpoint._get_fingerprint",
            return_value=Success(new_fingerprints),
        )
        mocker.patch(
            "gyomu_workflow.snapshot.checkpoint._get_checkpoint_path",
            return_value=Path("Checkpoint.json"),
        )
        mocker.patch.object(Path, "exists", return_value=True)
        mocker.patch(
            "gyomu_workflow.snapshot.checkpoint.read_json",
            return_value=Success(checkpoint),
        )

        result = load_checkpoint(
            request=snapshot_request,
            target=create_snapshot_target(),
        )

        assert isinstance(result, Success)
        updated = result.unwrap()
        assert updated is checkpoint
        assert updated.completed_steps == tuple()
        assert updated.fingerprints == new_fingerprints

    def test_initializes_checkpoint_when_reading_fails(
        self, snapshot_request, mocker
    ) -> None:
        fingerprints = create_fingerprints()
        mocker.patch(
            "gyomu_workflow.snapshot.checkpoint._get_fingerprint",
            return_value=Success(fingerprints),
        )
        mocker.patch(
            "gyomu_workflow.snapshot.checkpoint._get_checkpoint_path",
            return_value=Path("Checkpoint.json"),
        )
        mocker.patch.object(Path, "exists", return_value=True)
        mocker.patch(
            "gyomu_workflow.snapshot.checkpoint.read_json",
            return_value=Failure(
                GyomuError(
                    message="invalid checkpoint",
                    domain="snapshot",
                    operation="read",
                    reason="external_failure",
                    context="test",
                )
            ),
        )

        result = load_checkpoint(
            request=snapshot_request,
            target=create_snapshot_target(),
        )

        assert isinstance(result, Success)
        checkpoint = result.unwrap()
        assert checkpoint.package == snapshot_request.project_context.config.name
        assert checkpoint.completed_steps == tuple()
        assert checkpoint.fingerprints == fingerprints

    def test_returns_failure_when_fingerprint_creation_fails(
        self, snapshot_request, mocker
    ) -> None:
        error = GyomuError(
            message="failed to calculate fingerprint",
            domain="snapshot",
            operation="calculate fingerprint",
            reason="external_failure",
            context="test",
        )
        mocker.patch(
            "gyomu_workflow.snapshot.checkpoint._get_fingerprint",
            return_value=Failure(error),
        )

        result = load_checkpoint(
            request=snapshot_request,
            target=create_snapshot_target(),
        )

        assert isinstance(result, Failure)
        assert result.failure() is error


class TestToHashError:
    def test_converts_io_error_to_gyomu_error(self) -> None:
        io_error = GyomuIOError(
            message="file access failed",
            layer=IOLayer.FILESYSTEM,
            operation=IOOperation.READ,
            context="hash_file",
        )
        path = WorkspaceRelativePath(Path(".gyomu/knowledge/Package.yaml"))
        caller = "test_caller"

        result = _to_hash_error(err=io_error, path=path, caller=caller)

        assert result.message == f"fail to hash file: {path}"
        assert result.domain == "snapshot"
        assert result.operation == "calculate workspace hash"
        assert result.reason == "external_failure"
        assert result.context == caller


class TestCalculateWorkspaceHash:
    def test_calculates_hash_for_all_files(self, mocker) -> None:
        workspace_path = FullPath(Path("/workspace"))
        paths = (
            WorkspaceRelativePath(Path(".gyomu/knowledge/Technical.yaml")),
            WorkspaceRelativePath(Path(".gyomu/knowledge/Package.yaml")),
        )
        hash_by_path = {
            workspace_path / paths[0]: "TECHNICAL_HASH",
            workspace_path / paths[1]: "PACKAGE_HASH",
        }
        hash_file = mocker.patch(
            "gyomu_workflow.snapshot.checkpoint.hash_file",
            side_effect=lambda path: Success(hash_by_path[path]),
        )
        expected_entries = tuple(
            sorted(
                (
                    (str(paths[0]), "TECHNICAL_HASH"),
                    (str(paths[1]), "PACKAGE_HASH"),
                )
            )
        )

        result = _calculate_workspace_hash(
            workspace_path=workspace_path,
            paths=paths,
        )

        assert isinstance(result, Success)
        assert result.unwrap() == hash_object(expected_entries)
        assert hash_file.call_count == 2
        hash_file.assert_any_call(workspace_path / paths[0])
        hash_file.assert_any_call(workspace_path / paths[1])

    def test_calculates_hash_for_empty_files(self, mocker) -> None:
        hash_file = mocker.patch("gyomu_workflow.snapshot.checkpoint.hash_file")

        result = _calculate_workspace_hash(
            workspace_path=FullPath(Path("/workspace")),
            paths=tuple(),
        )

        assert isinstance(result, Success)
        assert result.unwrap() == hash_object(tuple())
        hash_file.assert_not_called()

    def test_returns_failure_when_hash_file_fails(self, mocker) -> None:
        workspace_path = FullPath(Path("/workspace"))
        path = WorkspaceRelativePath(Path(".gyomu/knowledge/Package.yaml"))
        io_error = GyomuIOError(
            message="file access failed",
            layer=IOLayer.FILESYSTEM,
            operation=IOOperation.READ,
            context="hash_file",
        )
        mocker.patch(
            "gyomu_workflow.snapshot.checkpoint.hash_file",
            return_value=Failure(io_error),
        )

        result = _calculate_workspace_hash(
            workspace_path=workspace_path,
            paths=(path,),
        )

        assert isinstance(result, Failure)
        error = result.failure()
        assert error.message == f"fail to hash file: {path}"
        assert error.domain == "snapshot"
        assert error.operation == "calculate workspace hash"


class TestGetWorkspaceFingerprint:
    def test_creates_fingerprint(self, snapshot_request, mocker) -> None:
        paths = (
            WorkspaceRelativePath(Path(".gyomu/knowledge/Package.yaml")),
            WorkspaceRelativePath(Path(".gyomu/knowledge/Technical.yaml")),
        )
        mocker.patch(
            "gyomu_workflow.snapshot.checkpoint.enumerate_workspace_target_files",
            return_value=paths,
        )
        calculate_hash = mocker.patch(
            "gyomu_workflow.snapshot.checkpoint._calculate_workspace_hash",
            return_value=Success("WORKSPACE_HASH"),
        )

        result = _get_workspace_fingerprint(snapshot_request)

        assert isinstance(result, Success)
        assert result.unwrap() == InputFingerprint(
            paths=paths,
            hash="WORKSPACE_HASH",
        )
        calculate_hash.assert_called_once_with(
            workspace_path=snapshot_request.workspace.path,
            paths=paths,
        )

    def test_returns_failure_when_hash_calculation_fails(
        self, snapshot_request, mocker
    ) -> None:
        paths = (WorkspaceRelativePath(Path(".gyomu/knowledge/Package.yaml")),)
        error = GyomuError(
            message="failed to calculate workspace hash",
            domain="snapshot",
            operation="calculate workspace hash",
            reason="external_failure",
            context="test",
        )
        mocker.patch(
            "gyomu_workflow.snapshot.checkpoint.enumerate_workspace_target_files",
            return_value=paths,
        )
        mocker.patch(
            "gyomu_workflow.snapshot.checkpoint._calculate_workspace_hash",
            return_value=Failure(error),
        )

        result = _get_workspace_fingerprint(snapshot_request)

        assert isinstance(result, Failure)
        assert result.failure() is error


class TestUpdateCheckpoint:
    def test_adds_step_and_saves_checkpoint(self, snapshot_request, mocker):
        target = create_snapshot_target()
        checkpoint = create_checkpoint(
            package="test-package",
            completed_steps=(PipelineStep.DOCSTRING,),
        )
        fingerprints = create_fingerprints()

        get_fingerprint = mocker.patch(
            "gyomu_workflow.snapshot.checkpoint._get_fingerprint",
            return_value=Success(fingerprints),
        )
        save = mocker.patch(
            "gyomu_workflow.snapshot.checkpoint.write_json",
            return_value=Success(None),
        )

        result = update_checkpoint(
            checkpoint=checkpoint,
            request=snapshot_request,
            status_to_add=PipelineStep.DIRECTORY_CONCEPT,
            target=target,
        )

        assert isinstance(result, Success)
        updated = result.unwrap()

        assert updated == Checkpoint(
            package="test-package",
            completed_steps=(
                PipelineStep.DOCSTRING,
                PipelineStep.DIRECTORY_CONCEPT,
            ),
            fingerprints=fingerprints,
        )
        get_fingerprint.assert_called_once_with(
            request=snapshot_request,
            target=target,
        )
        save.assert_called_once_with(
            path=ANY,
            value=updated,
            value_type=Checkpoint,
        )

    def test_does_not_add_duplicate_step(self, snapshot_request, mocker):

        target = create_snapshot_target()
        checkpoint = create_checkpoint(
            completed_steps=(
                PipelineStep.DOCSTRING,
                PipelineStep.DIRECTORY_CONCEPT,
            ),
        )
        fingerprints = create_fingerprints()

        mocker.patch(
            "gyomu_workflow.snapshot.checkpoint._get_fingerprint",
            return_value=Success(fingerprints),
        )
        save = mocker.patch(
            "gyomu_workflow.snapshot.checkpoint.write_json",
            return_value=Success(None),
        )

        result = update_checkpoint(
            checkpoint=checkpoint,
            request=snapshot_request,
            status_to_add=PipelineStep.DOCSTRING,
            target=target,
        )

        assert isinstance(result, Success)
        updated = result.unwrap()

        assert updated.completed_steps == (
            PipelineStep.DOCSTRING,
            PipelineStep.DIRECTORY_CONCEPT,
        )
        save.assert_called_once_with(
            path=ANY,
            value=updated,
            value_type=Checkpoint,
        )

    def test_returns_failure_when_fingerprint_calculation_fails(
        self, snapshot_request, mocker
    ):

        target = create_snapshot_target()
        checkpoint = create_checkpoint()
        error = GyomuError(
            message="failed to calculate workspace hash",
            domain="snapshot",
            operation="calculate workspace hash",
            reason="external_failure",
            context="test",
        )
        mocker.patch(
            "gyomu_workflow.snapshot.checkpoint._get_fingerprint",
            return_value=Failure(error),
        )
        save = mocker.patch(
            "gyomu_workflow.snapshot.checkpoint.write_json",
        )

        result = update_checkpoint(
            checkpoint=checkpoint,
            request=snapshot_request,
            status_to_add=PipelineStep.DOCSTRING,
            target=target,
        )

        assert isinstance(result, Failure)
        assert result.failure() is error
        save.assert_not_called()

    def test_returns_gyomu_error_when_saving_fails(self, snapshot_request, mocker):

        target = create_snapshot_target()
        checkpoint = create_checkpoint()
        fingerprints = create_fingerprints()

        io_error = GyomuIOError(
            message="file access failed",
            layer=IOLayer.FILESYSTEM,
            operation=IOOperation.READ,
            context="hash_file",
        )

        mocker.patch(
            "gyomu_workflow.snapshot.checkpoint._get_fingerprint",
            return_value=Success(fingerprints),
        )
        mocker.patch(
            "gyomu_workflow.snapshot.checkpoint.write_json",
            return_value=Failure(io_error),
        )

        result = update_checkpoint(
            checkpoint=checkpoint,
            request=snapshot_request,
            status_to_add=PipelineStep.DOCSTRING,
            target=target,
        )

        assert isinstance(result, Failure)

        error = result.failure()
        assert error.message == "fail to update checkpoint"
        assert error.domain == "snapshot"
        assert error.operation == "update_checkpoint"
        assert error.reason == "external_failure"
