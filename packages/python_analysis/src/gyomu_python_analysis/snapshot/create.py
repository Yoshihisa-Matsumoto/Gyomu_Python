from datetime import UTC, datetime
from pathlib import Path

from gyomu_infra.filesystem.file_search import FileSearch
from gyomu_infra.hash.hash import hash_file
from gyomu_schema.filesystem.file import FileCompareType, FileFilterInfo, FileFilterType
from gyomu_schema.schemas.python.types import ProjectRelativePath, WorkspaceRelativePath
from gyomu_schema.schemas.types import FullPath
from returns.result import Failure, Result, Success

from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.snapshot.models import FileSnapshot, ProjectSnapshot


def create_snapshot(
    project_path: WorkspaceRelativePath,
    project_context: ProjectContext,
) -> Result[ProjectSnapshot, AnalysisError]:
    files: list[FileSnapshot] = []
    for entry in sorted(enumerate_target_files(project_context=project_context)):
        result = create_file_snapshot(project_context.project_root, entry)
        if isinstance(result, Failure):
            return result
        files.append(result.unwrap())
    return Success(
        ProjectSnapshot(
            project_root=project_path,
            files=tuple(files),
        )
    )


def enumerate_target_files(
    project_context: ProjectContext,
) -> frozenset[ProjectRelativePath]:
    files = set(project_context.included_files)
    files.add(ProjectRelativePath(Path("pyproject.toml")))
    concept_files = FileSearch.search(
        project_context.project_root,
        [
            FileFilterInfo(
                kind=FileFilterType.FILE_NAME,
                operator=FileCompareType.EQUAL,
                value=[".gyomu/knowledge/*"],
            )
        ],
    )
    for info in concept_files:
        files.add(
            ProjectRelativePath(
                info.full_path.relative_to(project_context.project_root)
            )
        )

    return frozenset(files)


def create_file_snapshot(
    project_full_path: FullPath, source_path: ProjectRelativePath
) -> Result[FileSnapshot, AnalysisError]:
    file_full_path = project_full_path / source_path
    result = hash_file(file_full_path).alt(
        lambda err: AnalysisError(
            "fail to hash file",
            file_path=file_full_path,
            phase="snapshot",
            context="gyomu_python_analysis.snapshot.create.create_file_snapshot",
        ).chain(err)
    )
    if isinstance(result, Failure):
        return result
    return Success(
        FileSnapshot(
            project_relative_path=source_path,
            raw_hash=result.unwrap(),
            modified_at=datetime.fromtimestamp(file_full_path.stat().st_mtime, tz=UTC),
        )
    )
