from pathlib import Path

import pytest
from gyomu_infra.hash.hash import short_sha256
from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_python_analysis.snapshot.project import (
    ProjectSnapshotWorkspace,
    ensure_project_workspace,
    to_project_id,
)
from gyomu_schema.error.io import GyomuIOError, IOLayer, IOOperation
from gyomu_schema.schemas.python.types import WorkspaceRelativePath
from gyomu_schema.schemas.types import FullPath
from pytest_mock import MockerFixture
from returns.result import Failure, Success


@pytest.mark.parametrize(
    ("project_path",),
    [
        (WorkspaceRelativePath(Path("packages/python_analysis")),),
        (WorkspaceRelativePath(Path("packages/docstring")),),
        (WorkspaceRelativePath(Path("src")),),
    ],
)
def test_to_project_id(project_path: WorkspaceRelativePath) -> None:
    result = to_project_id(project_path)

    assert result == short_sha256(str(project_path))


def test_ensure_project_workspace(
    mocker: MockerFixture,
    tmp_path: Path,
) -> None:
    repository_root_path = FullPath(tmp_path)
    project_path = WorkspaceRelativePath(Path("packages/python_analysis"))

    ensure_directory = mocker.patch(
        "gyomu_python_analysis.snapshot.project.ensure_directory",
        return_value=Success(None),
    )

    result = ensure_project_workspace(
        repository_root_path,
        project_path,
    )

    assert isinstance(result, Success)

    workspace = result.unwrap()

    expected_project_id = to_project_id(project_path)
    expected_root = FullPath(tmp_path / ".gyomu" / "snapshot" / expected_project_id)
    expected_snapshot = FullPath(expected_root / "file-hashes.json")

    assert workspace == ProjectSnapshotWorkspace(
        project_id=expected_project_id,
        snapshot_root_path=expected_root,
        snapshot_path=expected_snapshot,
    )

    ensure_directory.assert_called_once_with(expected_root)


def test_ensure_project_workspace_returns_failure_when_directory_creation_fails(
    mocker: MockerFixture,
    tmp_path: Path,
) -> None:
    repository_root_path = FullPath(tmp_path)
    project_path = WorkspaceRelativePath(Path("packages/python_analysis"))

    io_error = GyomuIOError(
        "Failed to create directory.",
        layer=IOLayer.FILESYSTEM,
        operation=IOOperation.WRITE,
    )

    mocker.patch(
        "gyomu_python_analysis.snapshot.project.ensure_directory",
        return_value=Failure(io_error),
    )

    result = ensure_project_workspace(
        repository_root_path,
        project_path,
    )

    assert isinstance(result, Failure)

    error = result.failure()

    assert isinstance(error, AnalysisError)
    assert error.message == "fail to prepare project snapshot folder"
    assert error.phase == "snapshot"
    assert error.context == "gyomu_python_analysis.snapshot.project.ensure_workspace"
