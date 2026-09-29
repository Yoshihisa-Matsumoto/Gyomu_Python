from pathlib import Path

from gyomu_python_analysis.analysis.initialize import initialize_project_context
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.schemas.types import FullPath


def create_test_project_structure(
    project_root: Path,
    files: dict[str, str],
) -> ProjectContext:
    pyproject = """
[project]
name = "test-project"
version = "0.1.0"
requires-python = ">=3.13"
""".strip()

    (project_root / "pyproject.toml").write_text(pyproject)

    for relative_path, content in files.items():
        file_path = project_root / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)

    return initialize_project_context(
        project_root=FullPath(project_root),
        source_root=ProjectRelativePath(Path("src")),
    ).unwrap()
