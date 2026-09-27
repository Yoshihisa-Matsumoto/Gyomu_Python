from datetime import UTC, datetime
from pathlib import Path

from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_python_analysis.snapshot.commit import commit_project_changes
from gyomu_python_analysis.snapshot.models import (
    FileAdded,
    FileDeleted,
    FileSnapshot,
    FileUpdated,
    ProjectSnapshot,
)
from gyomu_schema.error.io import GyomuIOError, IOLayer, IOOperation
from gyomu_schema.schemas.python.types import ProjectRelativePath, WorkspaceRelativePath
from gyomu_schema.schemas.types import FullPath
from returns.result import Failure, Success


def create_snapshot(
    project_path: WorkspaceRelativePath,
    *files: FileSnapshot,
) -> ProjectSnapshot:
    return ProjectSnapshot(
        project_root=project_path,
        files=files,
    )


def create_file_snapshot(
    path: str,
    raw_hash: str = "hash",
) -> FileSnapshot:
    return FileSnapshot(
        project_relative_path=ProjectRelativePath(Path(path)),
        raw_hash=raw_hash,
        modified_at=datetime(2026, 9, 22, tzinfo=UTC),
    )


def test_commit_project_changes_success(
    mocker,
    tmp_path,
):
    repository_root_path = FullPath(tmp_path)
    project_root = FullPath(tmp_path / "packages" / "example")
    project_path = WorkspaceRelativePath(Path("packages/example"))
    snapshot_path = FullPath(tmp_path / "snapshot.json")

    project_context = mocker.Mock()
    project_context.project_root = project_root

    expected_snapshot = create_snapshot(
        project_path,
        create_file_snapshot("src/a.py", "aaa"),
    )
    current_snapshot = create_snapshot(
        project_path,
        create_file_snapshot("src/a.py", "aaa"),
    )

    workspace = mocker.Mock()
    workspace.project_id = "project-id"
    workspace.snapshot_path = snapshot_path

    mock_ensure = mocker.patch(
        "gyomu_python_analysis.snapshot.commit.ensure_project_workspace",
        return_value=Success(workspace),
    )
    mock_create = mocker.patch(
        "gyomu_python_analysis.snapshot.commit.create_snapshot",
        return_value=Success(current_snapshot),
    )
    mock_diff = mocker.patch(
        "gyomu_python_analysis.snapshot.commit.diff_snapshot",
        return_value=(),
    )
    mock_write = mocker.patch(
        "gyomu_python_analysis.snapshot.commit.write_json",
        return_value=Success(None),
    )

    result = commit_project_changes(
        repository_root_path=repository_root_path,
        project_context=project_context,
        expected_snapshot=expected_snapshot,
    )

    assert isinstance(result, Success)
    assert result.unwrap() is None

    mock_ensure.assert_called_once_with(
        repository_root_path,
        project_path,
    )
    mock_create.assert_called_once_with(
        project_context=project_context,
        project_path=project_path,
    )
    mock_diff.assert_called_once_with(
        previous=expected_snapshot,
        current=current_snapshot,
    )
    mock_write.assert_called_once_with(
        path=snapshot_path,
        value_type=ProjectSnapshot,
        value=current_snapshot,
    )


def test_commit_project_changes_detects_changes(
    mocker,
    tmp_path,
):
    repository_root_path = FullPath(tmp_path)
    project_root = FullPath(tmp_path / "packages" / "example")
    project_path = WorkspaceRelativePath(Path("packages/example"))
    snapshot_path = FullPath(tmp_path / "snapshot.json")

    project_context = mocker.Mock()
    project_context.project_root = project_root

    expected_snapshot = create_snapshot(
        project_path,
        create_file_snapshot("src/a.py", "aaa"),
        create_file_snapshot("src/b.py", "bbb"),
        create_file_snapshot("src/c.py", "ccc"),
    )

    current_snapshot = create_snapshot(
        project_path,
        create_file_snapshot("src/a.py", "aaa"),
        create_file_snapshot("src/b.py", "bbb-new"),
        create_file_snapshot("src/d.py", "ddd"),
    )

    diff = (
        FileUpdated(
            project_relative_path=ProjectRelativePath(Path("src/b.py")),
            previous=expected_snapshot.files[1],
            current=current_snapshot.files[1],
        ),
        FileDeleted(
            project_relative_path=ProjectRelativePath(Path("src/c.py")),
            previous=expected_snapshot.files[2],
        ),
        FileAdded(
            project_relative_path=ProjectRelativePath(Path("src/d.py")),
            current=current_snapshot.files[2],
        ),
    )

    workspace = mocker.Mock()
    workspace.snapshot_path = snapshot_path

    mocker.patch(
        "gyomu_python_analysis.snapshot.commit.ensure_project_workspace",
        return_value=Success(workspace),
    )
    mocker.patch(
        "gyomu_python_analysis.snapshot.commit.create_snapshot",
        return_value=Success(current_snapshot),
    )
    mocker.patch(
        "gyomu_python_analysis.snapshot.commit.diff_snapshot",
        return_value=diff,
    )
    mock_write = mocker.patch(
        "gyomu_python_analysis.snapshot.commit.write_json",
    )

    result = commit_project_changes(
        repository_root_path=repository_root_path,
        project_context=project_context,
        expected_snapshot=expected_snapshot,
    )

    assert isinstance(result, Failure)

    error = result.failure()
    assert isinstance(error, Exception)
    assert error.message == (
        "Snapshot diff detected. Project was modified during execution."
    )
    assert error.details == {
        "added": 1,
        "updated": 1,
        "deleted": 1,
    }

    mock_write.assert_not_called()


def test_commit_project_changes_returns_workspace_failure(
    mocker,
    tmp_path,
):
    repository_root_path = FullPath(tmp_path)
    project_root = FullPath(tmp_path / "packages" / "example")

    project_context = mocker.Mock()
    project_context.project_root = project_root

    expected_snapshot = ProjectSnapshot(
        project_root=WorkspaceRelativePath(Path("packages/example")),
        files=(),
    )

    error = AnalysisError("workspace error", file_path=project_root, phase="snapshot")

    mock_ensure = mocker.patch(
        "gyomu_python_analysis.snapshot.commit.ensure_project_workspace",
        return_value=Failure(error),
    )
    mock_create = mocker.patch(
        "gyomu_python_analysis.snapshot.commit.create_snapshot",
    )

    result = commit_project_changes(
        repository_root_path=repository_root_path,
        project_context=project_context,
        expected_snapshot=expected_snapshot,
    )

    assert isinstance(result, Failure)
    assert result.failure() is error

    mock_ensure.assert_called_once()
    mock_create.assert_not_called()


def test_commit_project_changes_returns_create_snapshot_failure(
    mocker,
    tmp_path,
):
    repository_root_path = FullPath(tmp_path)
    project_root = FullPath(tmp_path / "packages" / "example")
    project_path = WorkspaceRelativePath(Path("packages/example"))

    project_context = mocker.Mock()
    project_context.project_root = project_root

    expected_snapshot = ProjectSnapshot(
        project_root=project_path,
        files=(),
    )

    workspace = mocker.Mock()
    workspace.snapshot_path = FullPath(tmp_path / "snapshot.json")

    error = AnalysisError("create error", file_path=project_root, phase="snapshot")

    mocker.patch(
        "gyomu_python_analysis.snapshot.commit.ensure_project_workspace",
        return_value=Success(workspace),
    )
    mock_create = mocker.patch(
        "gyomu_python_analysis.snapshot.commit.create_snapshot",
        return_value=Failure(error),
    )
    mock_write = mocker.patch(
        "gyomu_python_analysis.snapshot.commit.write_json",
    )

    result = commit_project_changes(
        repository_root_path=repository_root_path,
        project_context=project_context,
        expected_snapshot=expected_snapshot,
    )

    assert isinstance(result, Failure)
    assert result.failure() is error

    mock_create.assert_called_once()
    mock_write.assert_not_called()


def test_commit_project_changes_returns_write_failure(
    mocker,
    tmp_path,
):
    repository_root_path = FullPath(tmp_path)
    project_root = FullPath(tmp_path / "packages" / "example")
    project_path = WorkspaceRelativePath(Path("packages/example"))
    snapshot_path = FullPath(tmp_path / "snapshot.json")

    project_context = mocker.Mock()
    project_context.project_root = project_root

    expected_snapshot = ProjectSnapshot(
        project_root=project_path,
        files=(),
    )
    current_snapshot = ProjectSnapshot(
        project_root=project_path,
        files=(),
    )

    workspace = mocker.Mock()
    workspace.snapshot_path = snapshot_path

    write_error = GyomuIOError(
        message="Test", layer=IOLayer.FILESYSTEM, operation=IOOperation.WRITE
    )

    mocker.patch(
        "gyomu_python_analysis.snapshot.commit.ensure_project_workspace",
        return_value=Success(workspace),
    )
    mocker.patch(
        "gyomu_python_analysis.snapshot.commit.create_snapshot",
        return_value=Success(current_snapshot),
    )
    mocker.patch(
        "gyomu_python_analysis.snapshot.commit.diff_snapshot",
        return_value=(),
    )
    mocker.patch(
        "gyomu_python_analysis.snapshot.commit.write_json",
        return_value=Failure(write_error),
    )

    result = commit_project_changes(
        repository_root_path=repository_root_path,
        project_context=project_context,
        expected_snapshot=expected_snapshot,
    )

    assert isinstance(result, Failure)

    error = result.failure()
    assert error.message == "fail to write project snapshot"
    assert error.file_path == snapshot_path
