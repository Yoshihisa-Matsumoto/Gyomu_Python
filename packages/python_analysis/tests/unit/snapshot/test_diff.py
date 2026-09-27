from datetime import UTC, datetime
from pathlib import Path

from gyomu_python_analysis.snapshot.diff import diff_snapshot
from gyomu_python_analysis.snapshot.models import (
    FileAdded,
    FileDeleted,
    FileSnapshot,
    FileUpdated,
    ProjectSnapshot,
)
from gyomu_schema.schemas.python.types import ProjectRelativePath, WorkspaceRelativePath

PROJECT_ROOT = WorkspaceRelativePath(Path("packages/example"))

FILE_A = ProjectRelativePath(Path("src/a.py"))
FILE_B = ProjectRelativePath(Path("src/b.py"))
FILE_C = ProjectRelativePath(Path("src/c.py"))
FILE_D = ProjectRelativePath(Path("src/d.py"))


def create_file_snapshot(
    path: ProjectRelativePath,
    raw_hash: str,
) -> FileSnapshot:
    return FileSnapshot(
        project_relative_path=path,
        raw_hash=raw_hash,
        modified_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


def create_project_snapshot(
    *files: FileSnapshot,
) -> ProjectSnapshot:
    return ProjectSnapshot(
        project_root=PROJECT_ROOT,
        files=files,
    )


def test_diff_snapshot_unchanged():
    previous_file = create_file_snapshot(FILE_A, "hash-a")
    current_file = create_file_snapshot(FILE_A, "hash-a")

    previous = create_project_snapshot(previous_file)
    current = create_project_snapshot(current_file)

    result = diff_snapshot(previous, current)

    assert result == ()


def test_diff_snapshot_unchanged_when_only_modified_at_changed():
    previous_file = create_file_snapshot(FILE_A, "hash-a")
    current_file = FileSnapshot(
        project_relative_path=FILE_A,
        raw_hash="hash-a",
        modified_at=datetime(2026, 2, 1, tzinfo=UTC),
    )

    result = diff_snapshot(
        create_project_snapshot(previous_file),
        create_project_snapshot(current_file),
    )

    assert result == ()


def test_diff_snapshot_added():
    current_file = create_file_snapshot(FILE_A, "hash-a")

    result = diff_snapshot(
        create_project_snapshot(),
        create_project_snapshot(current_file),
    )

    assert result == (
        FileAdded(
            project_relative_path=FILE_A,
            current=current_file,
        ),
    )


def test_diff_snapshot_deleted():
    previous_file = create_file_snapshot(FILE_A, "hash-a")

    result = diff_snapshot(
        create_project_snapshot(previous_file),
        create_project_snapshot(),
    )

    assert result == (
        FileDeleted(
            project_relative_path=FILE_A,
            previous=previous_file,
        ),
    )


def test_diff_snapshot_updated():
    previous_file = create_file_snapshot(FILE_A, "hash-a")
    current_file = create_file_snapshot(FILE_A, "hash-b")

    result = diff_snapshot(
        create_project_snapshot(previous_file),
        create_project_snapshot(current_file),
    )

    assert result == (
        FileUpdated(
            project_relative_path=FILE_A,
            previous=previous_file,
            current=current_file,
        ),
    )


def test_diff_snapshot_multiple_changes_are_sorted():
    previous_a = create_file_snapshot(FILE_A, "hash-a")
    previous_b = create_file_snapshot(FILE_B, "hash-b")
    previous_c = create_file_snapshot(FILE_C, "hash-c")

    current_a = create_file_snapshot(FILE_A, "hash-a-updated")
    current_d = create_file_snapshot(FILE_D, "hash-d")

    previous = create_project_snapshot(
        previous_c,
        previous_a,
        previous_b,
    )
    current = create_project_snapshot(
        current_d,
        current_a,
    )

    result = diff_snapshot(previous, current)

    assert result == (
        FileUpdated(
            project_relative_path=FILE_A,
            previous=previous_a,
            current=current_a,
        ),
        FileDeleted(
            project_relative_path=FILE_B,
            previous=previous_b,
        ),
        FileDeleted(
            project_relative_path=FILE_C,
            previous=previous_c,
        ),
        FileAdded(
            project_relative_path=FILE_D,
            current=current_d,
        ),
    )
