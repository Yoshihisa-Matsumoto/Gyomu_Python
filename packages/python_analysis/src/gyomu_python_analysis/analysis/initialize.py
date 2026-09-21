import ast
from pathlib import Path
from tomllib import loads
from typing import Any

from gyomu_infra.filesystem.file_io import enumerate_files, read_text
from gyomu_schema.schemas.python.types import (
    ProjectRelativePath,
    PythonPath,
    WorkspaceRelativePath,
)
from gyomu_schema.schemas.types import FullPath
from returns.result import Failure, Result, Success

from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_python_analysis.project.context import ProjectContext, PyProjectConfig
from gyomu_python_analysis.project.workspace import WorkspaceConfig, WorkspaceProject


def resolve_source_root(project_root: FullPath) -> ProjectRelativePath:
    if (project_root / "src").is_dir():
        return ProjectRelativePath(Path("src"))

    return ProjectRelativePath(Path("."))


def initialize_project_from_workspace(
    workspace: WorkspaceConfig, project: WorkspaceProject
) -> ProjectContext:
    project_root = FullPath(workspace.path / project.path)
    source_root = resolve_source_root(project_root)
    files = find_included_python_files(
        project_root=project_root, source_root=source_root
    )
    return ProjectContext(
        project_root=project_root,
        source_root=source_root,
        config=project.config,
        included_files=files,
    )


def initialize_project_context(
    project_root: FullPath, source_root: ProjectRelativePath
) -> Result[ProjectContext, AnalysisError]:
    pyproject_path = project_root / "pyproject.toml"
    read_result = read_text(pyproject_path)
    if isinstance(read_result, Failure):
        return Failure(
            AnalysisError(
                "fail to read pyproject.toml",
                file_path=PythonPath(""),
                phase="project-load",
                context="gyomu_python_analysis.analysis.initialize.initialize_project_context",
            ).chain(read_result.failure())
        )
    toml_data = loads(read_result.unwrap())
    # print(repr(toml_data))
    config_result = analyze_project_config(
        project_root=project_root, toml_data=toml_data
    )
    if isinstance(config_result, Failure):
        return config_result

    files = find_included_python_files(
        project_root=project_root, source_root=source_root
    )
    return Success(
        ProjectContext(
            project_root=project_root,
            source_root=source_root,
            config=config_result.unwrap(),
            included_files=files,
        )
    )


def find_included_python_files(
    project_root: FullPath, source_root: ProjectRelativePath
) -> frozenset[ProjectRelativePath]:
    source_path = project_root / source_root
    files = enumerate_files(source_path, _is_python_source_file, project_root)
    return frozenset(ProjectRelativePath(path) for path in files)


def _is_python_source_file(path: Path) -> bool:
    return path.suffix == ".py" and not _is_test_file(path)


def _is_test_file(path: Path) -> bool:
    return path.name.startswith("test_") or path.name.endswith("_test.py")


def analyze_project_config(
    project_root: FullPath,
    toml_data: dict[str, Any],
    project_relative_path: WorkspaceRelativePath | None = None,
    workspace_config: WorkspaceConfig | None = None,
) -> Result[PyProjectConfig, AnalysisError]:
    if project_relative_path is None:
        project_relative_path = WorkspaceRelativePath(Path("."))
    project = toml_data["project"]
    name = project.get("name", "")
    description = project.get("description", None)
    is_version_dynamic = "dynamic" in project and "version" in project["dynamic"]
    version = project.get("version", "")
    # print(version)
    # print(is_version_dynamic)
    if is_version_dynamic:
        backend = toml_data["build-system"]["requires"]
        # print(backend)
        if "hatchling" in backend:
            version_path = (
                None
                if "tool" not in toml_data
                else toml_data["tool"]["hatch"]["version"]["path"]
            )
            # print(version_path)
            if isinstance(version_path, str):
                version_result = read_version(project_root / Path(version_path))
                if isinstance(version_result, Failure):
                    return version_result
                version = version_result.unwrap()

    formatter_line_length: int | None = None
    tool = toml_data.get("tool")
    if (
        isinstance(tool, dict)
        and isinstance(tool.get("ruff"), dict)
        and "line-length" in tool["ruff"]
    ):
        formatter_line_length = int(tool["ruff"]["line-length"])
    if formatter_line_length is None:
        formatter_line_length = (
            workspace_config.formatter_line_length
            if workspace_config is not None
            else 88
        )
    return Success(
        PyProjectConfig(
            name=name,
            description=description,
            version=str(version),
            formatter_line_length=formatter_line_length,
            path=project_relative_path,
        )
    )


def read_version(path: Path) -> Result[str | None, AnalysisError]:
    # print(path)
    source_result = read_text(path)
    if isinstance(source_result, Failure):
        return Failure(
            AnalysisError(
                "fail to read version file",
                file_path=PythonPath(""),
                phase="project-load",
                context="gyomu_python_analysis.analysis.initialize.read_version",
                details={"path": path},
            )
        )
    tree = ast.parse(source_result.unwrap(), filename=str(path))

    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "__version__"
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ):
            return Success(node.value.value)

    return Success(None)


# if __name__ == "__main__":
#     result = initialize_project_context(
#         project_root=FullPath(
#             Path("c:/data/program/python/gyomu-python/packages/docstring")
#         ),
#         source_root=ProjectRelativePath(Path("./src")),
#     )
#     if isinstance(result, Success):
#         print("Success")
#     else:
#         print(repr(result.failure()))
