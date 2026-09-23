from gyomu_schema.schemas.python.types import ProjectRelativePath

from gyomu_python_analysis.snapshot.models import (
    FileAdded,
    FileChange,
    FileDeleted,
    FileSnapshot,
    FileUpdated,
    ProjectSnapshot,
)


def to_map(
    snapshot: ProjectSnapshot,
) -> dict[ProjectRelativePath, FileSnapshot]:
    return {file.project_relative_path: file for file in snapshot.files}


def diff_snapshot(
    previous: ProjectSnapshot, current: ProjectSnapshot
) -> tuple[FileChange, ...]:
    previous_files = to_map(previous)
    current_files = to_map(current)

    changes: list[FileChange] = []

    for path, previous_file in previous_files.items():
        current_file = current_files.get(path)

        if current_file is None:
            changes.append(
                FileDeleted(project_relative_path=path, previous=previous_file)
            )
            continue

        if previous_file.raw_hash != current_file.raw_hash:
            changes.append(
                FileUpdated(
                    project_relative_path=path,
                    previous=previous_file,
                    current=current_file,
                )
            )

    for path, current_file in current_files.items():
        if path not in previous_files:
            changes.append(FileAdded(project_relative_path=path, current=current_file))

    return tuple(sorted(changes, key=lambda change: change.project_relative_path))
