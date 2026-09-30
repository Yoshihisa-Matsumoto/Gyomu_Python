from difflib import unified_diff
from pathlib import Path

from gyomu_python_analysis.analysis.initialize import initialize_project_context
from gyomu_python_analysis.analysis.workspace import initialize_workspace_context
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_schema.schemas.python.types import (
    ProjectRelativePath,
)
from gyomu_schema.schemas.types import FullPath

from packages.python_analysis.python_analysis_test_support.helpers import (
    create_workspace_root,
)

FIXTURES_ROOT = FullPath(Path(__file__).parent / "fixtures")


def assert_text_file_equals(
    root_path: Path, source_path: Path, expected_path: Path
) -> None:
    actual_path = root_path / source_path
    expected_path = root_path / expected_path
    actual = actual_path.read_text(encoding="utf-8")
    expected = expected_path.read_text(encoding="utf-8")

    diff = "".join(
        unified_diff(
            expected.splitlines(keepends=True),
            actual.splitlines(keepends=True),
            fromfile=str(expected_path),
            tofile=str(actual_path),
        )
    )

    assert actual == expected, f"\n{diff}"


def _create_directory_project_context() -> ProjectContext:
    return initialize_project_context(
        project_root=FIXTURES_ROOT / "directory",
        source_root=ProjectRelativePath(Path("src")),
    ).unwrap()


def create_workspace_context() -> WorkspaceContext:
    root = create_workspace_root(path=FIXTURES_ROOT / "monorepo")
    return initialize_workspace_context(root=root).unwrap()


def create_monorepo_project_context(project_name: str) -> ProjectContext:
    return initialize_project_context(
        project_root=FIXTURES_ROOT / "monorepo" / "packages" / project_name,
        source_root=ProjectRelativePath(Path("src")),
    ).unwrap()
