from datetime import UTC, datetime
from pathlib import Path

import pytest
from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.snapshot.create import (
    create_file_snapshot,
    create_snapshot,
    enumerate_target_files,
)
from gyomu_python_analysis.snapshot.models import FileSnapshot, ProjectSnapshot
from gyomu_schema.error.io import GyomuIOError, IOLayer, IOOperation
from gyomu_schema.schemas.python.types import ProjectRelativePath, WorkspaceRelativePath
from gyomu_schema.schemas.types import FullPath
from returns.result import Failure, Success

from packages.python_analysis.python_analysis_test_support.helpers import (
    _create_context,
)


@pytest.fixture
def project_context() -> ProjectContext:
    return _create_context()


def test_create_file_snapshot_success(mocker):
    project_root = FullPath(Path("/project"))
    source_path = ProjectRelativePath(Path("src/example.py"))
    file_path = project_root / source_path

    mock_hash_file = mocker.patch(
        "gyomu_python_analysis.snapshot.create.hash_file",
        return_value=Success("abc123"),
    )
    mock_stat = mocker.patch(
        "gyomu_python_analysis.snapshot.create.Path.stat",
        return_value=mocker.Mock(st_mtime=1_757_000_000),
    )

    result = create_file_snapshot(project_root, source_path)

    assert isinstance(result, Success)

    snapshot = result.unwrap()
    assert snapshot == FileSnapshot(
        project_relative_path=source_path,
        raw_hash="abc123",
        modified_at=datetime.fromtimestamp(
            1_757_000_000,
            tz=UTC,
        ),
    )

    mock_hash_file.assert_called_once_with(file_path)
    mock_stat.assert_called_once_with()


def test_create_file_snapshot_hash_failure(mocker):
    project_root = FullPath(Path("/project"))
    source_path = ProjectRelativePath(Path("src/example.py"))
    file_path = project_root / source_path

    original_error = GyomuIOError(
        message="fail to hash", layer=IOLayer.FILESYSTEM, operation=IOOperation.READ
    )

    mocker.patch(
        "gyomu_python_analysis.snapshot.create.hash_file",
        return_value=Failure(original_error),
    )

    result = create_file_snapshot(project_root, source_path)

    assert isinstance(result, Failure)

    error = result.failure()
    assert error.message == "fail to hash file"
    assert error.file_path == file_path
    assert error.phase == "snapshot"
    assert error.context == "gyomu_python_analysis.snapshot.create.create_file_snapshot"


def test_enumerate_target_files(mocker, project_context):
    knowledge_file = mocker.Mock()
    knowledge_file.full_path = (
        project_context.project_root / ".gyomu/knowledge/example.md"
    )

    mocker.patch(
        "gyomu_python_analysis.snapshot.create.FileSearch.search",
        return_value=[knowledge_file],
    )

    result = enumerate_target_files(project_context)

    assert result == frozenset(
        {
            *project_context.included_files,
            ProjectRelativePath(Path("pyproject.toml")),
            ProjectRelativePath(Path(".gyomu/knowledge/example.md")),
        }
    )


def test_create_snapshot(mocker, project_context):
    project_path = WorkspaceRelativePath(Path("packages/example"))

    file1 = ProjectRelativePath(Path("src/a.py"))
    file2 = ProjectRelativePath(Path("src/b.py"))

    snapshot1 = FileSnapshot(
        project_relative_path=file1,
        raw_hash="hash-a",
        modified_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    snapshot2 = FileSnapshot(
        project_relative_path=file2,
        raw_hash="hash-b",
        modified_at=datetime(2026, 1, 2, tzinfo=UTC),
    )

    mocker.patch(
        "gyomu_python_analysis.snapshot.create.enumerate_target_files",
        return_value=frozenset({file1, file2}),
    )
    mock_create = mocker.patch(
        "gyomu_python_analysis.snapshot.create.create_file_snapshot",
        side_effect=[Success(snapshot1), Success(snapshot2)],
    )

    result = create_snapshot(project_path, project_context)

    assert isinstance(result, Success)
    assert result.unwrap() == ProjectSnapshot(
        project_root=project_path,
        files=(snapshot1, snapshot2),
    )
    assert mock_create.call_count == 2


def test_create_snapshot_hash_failure(mocker, project_context):
    project_path = WorkspaceRelativePath(Path("packages/example"))

    file1 = ProjectRelativePath(Path("src/a.py"))

    mocker.patch(
        "gyomu_python_analysis.snapshot.create.enumerate_target_files",
        return_value=frozenset({file1}),
    )

    original_error = GyomuIOError(
        message="fail to hash", layer=IOLayer.FILESYSTEM, operation=IOOperation.READ
    )

    mocker.patch(
        "gyomu_python_analysis.snapshot.create.hash_file",
        return_value=Failure(original_error),
    )

    result = create_snapshot(project_path, project_context)

    assert isinstance(result, Failure)

    error = result.failure()
    assert isinstance(error, AnalysisError)
    assert error.context == "gyomu_python_analysis.snapshot.create.create_file_snapshot"
