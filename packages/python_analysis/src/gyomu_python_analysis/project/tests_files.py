from pathlib import Path

from gyomu_infra.filesystem.file_io import enumerate_files
from gyomu_schema.schemas.python.types import ProjectRelativePath, WorkspaceRelativePath

from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import WorkspaceContext

TEST_DEFAULT_PATH = ProjectRelativePath(Path("tests"))


def enumerate_test_files(
    workspace_context: WorkspaceContext,
    project_context: ProjectContext,
    test_path: ProjectRelativePath = TEST_DEFAULT_PATH,
) -> frozenset[WorkspaceRelativePath]:
    root_path = project_context.project_root / test_path
    files = enumerate_files(
        path=root_path,
        filter=_is_python_test_file,
        relative_to=workspace_context.workspace_root.path,
    )
    return frozenset(WorkspaceRelativePath(path) for path in files)


def _is_python_test_file(path: Path) -> bool:
    """Check if the given path is a Python file."""

    return path.suffix == ".py"
