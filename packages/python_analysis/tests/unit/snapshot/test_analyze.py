from pathlib import Path

from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_python_analysis.snapshot.analyze import analyze_project_changes
from gyomu_python_analysis.snapshot.models import (
    AnalyzeProjectChangesResult,
    ProjectSnapshot,
)
from gyomu_schema.schemas.python.types import WorkspaceRelativePath
from gyomu_schema.schemas.types import FullPath
from returns.result import Failure, Success


def create_project_context(
    mocker,
    repository_root: FullPath,
):
    project_root = repository_root / "packages" / "example"

    context = mocker.Mock()
    context.project_root = project_root
    return context


def test_analyze_project_changes_without_previous_snapshot(mocker):
    repository_root = FullPath(Path("/repository"))
    project_root = repository_root / "packages" / "example"

    project_context = mocker.Mock()
    project_context.project_root = project_root

    workspace = mocker.Mock()
    workspace.project_id = "project-id"
    workspace.snapshot_path = FullPath(
        project_root / ".gyomu" / "snapshot" / "project-id" / "file-hashes.json"
    )
    mocker.patch(
        "gyomu_python_analysis.snapshot.analyze.ensure_project_workspace",
        return_value=Success(workspace),
    )

    previous_snapshot = ProjectSnapshot(
        project_root=WorkspaceRelativePath(Path("packages/example")),
        files=(),
    )
    current_snapshot = ProjectSnapshot(
        project_root=WorkspaceRelativePath(Path("packages/example")),
        files=(),
    )

    mocker.patch(
        "gyomu_python_analysis.snapshot.analyze.create_snapshot",
        return_value=Success(current_snapshot),
    )
    mock_diff = mocker.patch(
        "gyomu_python_analysis.snapshot.analyze.diff_snapshot",
        return_value=(),
    )

    result = analyze_project_changes(repository_root, project_context)

    assert isinstance(result, Success)
    assert result.unwrap() == AnalyzeProjectChangesResult(
        project_id="project-id",
        snapshot_path=workspace.snapshot_path,
        previous_snapshot=None,
        current_snapshot=current_snapshot,
        diff=(),
    )

    mock_diff.assert_called_once_with(
        previous=previous_snapshot,
        current=current_snapshot,
    )


def test_analyze_project_changes_with_previous_snapshot(mocker, tmp_path):
    repository_root = FullPath(tmp_path)
    project_root = repository_root / "packages" / "example"

    project_root.mkdir(parents=True)

    project_context = mocker.Mock()
    project_context.project_root = project_root

    snapshot_path = FullPath(
        repository_root / ".gyomu" / "snapshot" / "project-id" / "file-hashes.json"
    )
    snapshot_path.parent.mkdir(parents=True)
    snapshot_path.touch()

    workspace = mocker.Mock()
    workspace.project_id = "project-id"
    workspace.snapshot_path = snapshot_path

    mocker.patch(
        "gyomu_python_analysis.snapshot.analyze.ensure_project_workspace",
        return_value=Success(workspace),
    )

    project_path = WorkspaceRelativePath(Path("packages/example"))

    previous_snapshot = ProjectSnapshot(
        project_root=project_path,
        files=(),
    )
    current_snapshot = ProjectSnapshot(
        project_root=project_path,
        files=(),
    )

    mock_read_json = mocker.patch(
        "gyomu_python_analysis.snapshot.analyze.read_json",
        return_value=Success(previous_snapshot),
    )
    mocker.patch(
        "gyomu_python_analysis.snapshot.analyze.create_snapshot",
        return_value=Success(current_snapshot),
    )
    mock_diff = mocker.patch(
        "gyomu_python_analysis.snapshot.analyze.diff_snapshot",
        return_value=(),
    )

    result = analyze_project_changes(repository_root, project_context)

    assert isinstance(result, Success)
    assert result.unwrap().previous_snapshot == previous_snapshot

    mock_read_json.assert_called_once_with(
        path=snapshot_path,
        model_type=ProjectSnapshot,
    )
    mock_diff.assert_called_once_with(
        previous=previous_snapshot,
        current=current_snapshot,
    )


def test_analyze_project_changes_workspace_failure(mocker):
    repository_root = FullPath(Path("/repository"))

    project_context = mocker.Mock()
    project_context.project_root = repository_root / "packages" / "example"

    error = AnalysisError(
        "workspace error",
        file_path=repository_root,
        phase="snapshot",
        context="test",
    )

    mocker.patch(
        "gyomu_python_analysis.snapshot.analyze.ensure_project_workspace",
        return_value=Failure(error),
    )
    mock_create = mocker.patch("gyomu_python_analysis.snapshot.analyze.create_snapshot")

    result = analyze_project_changes(repository_root, project_context)

    assert isinstance(result, Failure)
    assert result.failure() is error
    mock_create.assert_not_called()


def test_analyze_project_changes_read_snapshot_failure(mocker, tmp_path):
    repository_root = FullPath(tmp_path)
    project_root = repository_root / "packages" / "example"

    project_root.mkdir(parents=True)

    WorkspaceRelativePath(Path("packages/example"))

    snapshot_path = FullPath(
        repository_root / ".gyomu" / "snapshot" / "project-id" / "file-hashes.json"
    )
    snapshot_path.parent.mkdir(parents=True)
    snapshot_path.touch()

    project_context = mocker.Mock()
    project_context.project_root = project_root

    workspace = mocker.Mock()
    workspace.project_id = "project-id"
    workspace.snapshot_path = snapshot_path

    mocker.patch(
        "gyomu_python_analysis.snapshot.analyze.ensure_project_workspace",
        return_value=Success(workspace),
    )

    original_error = AnalysisError(
        "read error",
        file_path=snapshot_path,
        phase="snapshot",
        context="test",
    )

    mocker.patch(
        "gyomu_python_analysis.snapshot.analyze.read_json",
        return_value=Failure(original_error),
    )
    mock_create = mocker.patch("gyomu_python_analysis.snapshot.analyze.create_snapshot")

    result = analyze_project_changes(repository_root, project_context)

    assert isinstance(result, Failure)

    error = result.failure()
    assert error.message == "fail to read project snapshot"
    assert error.file_path == snapshot_path
    assert error.phase == "snapshot"
    assert (
        error.context
        == "gyomu_python_analysis.snapshot.analyze.analyze_project_changes"
    )

    mock_create.assert_not_called()


def test_analyze_project_changes_create_snapshot_failure(
    mocker,
    tmp_path,
):
    repository_root = FullPath(tmp_path)
    project_root = repository_root / "packages" / "example"
    project_root.mkdir(parents=True)

    project_context = mocker.Mock()
    project_context.project_root = project_root

    workspace = mocker.Mock()
    workspace.project_id = "project-id"
    workspace.snapshot_path = FullPath(
        repository_root / ".gyomu" / "snapshot" / "project-id" / "file-hashes.json"
    )

    mocker.patch(
        "gyomu_python_analysis.snapshot.analyze.ensure_project_workspace",
        return_value=Success(workspace),
    )

    error = AnalysisError(
        "create error",
        file_path=project_root,
        phase="snapshot",
        context="test",
    )

    mocker.patch(
        "gyomu_python_analysis.snapshot.analyze.create_snapshot",
        return_value=Failure(error),
    )

    result = analyze_project_changes(repository_root, project_context)

    assert isinstance(result, Failure)
    assert result.failure() is error


def test_analyze_project_changes_returns_diff(mocker, tmp_path):
    repository_root = FullPath(tmp_path)
    project_root = repository_root / "packages" / "example"
    project_root.mkdir(parents=True)

    project_context = mocker.Mock()
    project_context.project_root = project_root

    snapshot_path = FullPath(
        repository_root / ".gyomu" / "snapshot" / "project-id" / "file-hashes.json"
    )
    snapshot_path.parent.mkdir(parents=True)
    snapshot_path.touch()

    workspace = mocker.Mock()
    workspace.project_id = "project-id"
    workspace.snapshot_path = snapshot_path

    project_path = WorkspaceRelativePath(Path("packages/example"))

    previous_snapshot = ProjectSnapshot(
        project_root=project_path,
        files=(),
    )
    current_snapshot = ProjectSnapshot(
        project_root=project_path,
        files=(),
    )

    diff = (
        # 実際の FileChange をここに入れる
    )

    mocker.patch(
        "gyomu_python_analysis.snapshot.analyze.ensure_project_workspace",
        return_value=Success(workspace),
    )
    mocker.patch(
        "gyomu_python_analysis.snapshot.analyze.read_json",
        return_value=Success(previous_snapshot),
    )
    mocker.patch(
        "gyomu_python_analysis.snapshot.analyze.create_snapshot",
        return_value=Success(current_snapshot),
    )
    mocker.patch(
        "gyomu_python_analysis.snapshot.analyze.diff_snapshot",
        return_value=diff,
    )

    result = analyze_project_changes(repository_root, project_context)

    assert isinstance(result, Success)

    assert result.unwrap().project_id == "project-id"
    assert result.unwrap().snapshot_path == snapshot_path
    assert result.unwrap().previous_snapshot == previous_snapshot
    assert result.unwrap().current_snapshot == current_snapshot
    assert result.unwrap().diff == diff
