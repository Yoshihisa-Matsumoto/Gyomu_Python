from pathlib import Path
from tomllib import loads
from typing import Any

from gyomu_infra.filesystem.file_io import read_text
from gyomu_schema.schemas.python.types import PythonPath, WorkspaceRelativePath
from gyomu_schema.schemas.types import FullPath
from returns.result import Failure, Result, Success

from gyomu_python_analysis.analysis.initialize import analyze_project_config
from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_python_analysis.project.workspace import (
    WorkspaceConfig,
    WorkspaceContext,
    WorkspaceProject,
    WorkspaceRoot,
    WorkspaceRootKind,
)


def find_root(
    start_directory: FullPath,
) -> Result[WorkspaceRoot, AnalysisError]:
    current = start_directory
    first_pyproject: FullPath | None = None

    while True:
        pyproject_path = current / "pyproject.toml"

        if pyproject_path.is_file():
            if first_pyproject is None:
                first_pyproject = current

            toml_result = read_pyproject_toml(pyproject_path)
            if isinstance(toml_result, Failure):
                return toml_result
            toml_data = toml_result.unwrap()
            if is_uv_workspace(toml_data):
                return Success(
                    WorkspaceRoot(path=current, kind=WorkspaceRootKind.UV_WORKSPACE)
                )

        parent = current.parent

        if parent == current:
            break

        current = FullPath(parent)

    if first_pyproject is not None:
        return Success(
            WorkspaceRoot(
                path=first_pyproject, kind=WorkspaceRootKind.STANDALONE_PROJECT
            )
        )

    return Failure(
        AnalysisError(
            "pyproject.toml not found",
            file_path=PythonPath(""),
            phase="workspace-discovery",
            context="gyomu_python_analysis.analysis.workspace.find_workspace_root",
        )
    )


def read_pyproject_toml(
    path: FullPath,
) -> Result[dict[str, Any], AnalysisError]:
    read_result = read_text(path)
    if isinstance(read_result, Failure):
        return Failure(
            AnalysisError(
                "fail to read pyproject.toml",
                file_path=path,
                phase="workspace-discovery",
                context=(
                    "gyomu_python_analysis.analysis.workspace.read_pyproject_toml"
                ),
            ).chain(read_result.failure())
        )

    return Success(loads(read_result.unwrap()))


def is_uv_workspace(toml_data: dict[str, Any]) -> bool:
    tool = toml_data.get("tool")
    if not isinstance(tool, dict):
        return False

    return isinstance(tool.get("uv"), dict) and isinstance(
        tool["uv"].get("workspace"), dict
    )


def initialize_workspace_config(
    path: FullPath, toml_data: dict[str, Any]
) -> Result[WorkspaceConfig, AnalysisError]:
    try:
        name = None
        description = None
        if "project" in toml_data:
            project = toml_data["project"]
            name = project.get("name", None)
            description = project.get("description", None)

        formatter_line_length: int | None = None
        tool = toml_data.get("tool")
        if (
            isinstance(tool, dict)
            and isinstance(tool.get("ruff"), dict)
            and "line-length" in tool["ruff"]
        ):
            formatter_line_length = int(tool["ruff"]["line-length"])

        if formatter_line_length is None:
            formatter_line_length = 88

        return Success(
            WorkspaceConfig(
                path=path,
                name=name,
                description=description,
                formatter_line_length=formatter_line_length,
            )
        )
    except ValueError:
        return Failure(
            AnalysisError(
                "fail to parse root pyproject.toml",
                file_path=path,
                phase="workspace-discovery",
                context="gyomu_python_analysis.analysis.workspace.intialize_workspace_config",
            )
        )


def get_uv_workspace_members(toml_data: dict[str, Any]) -> list[str]:
    tool = toml_data.get("tool")
    if not isinstance(tool, dict):
        return []

    if isinstance(tool.get("uv"), dict) and isinstance(
        tool["uv"].get("workspace"), dict
    ):
        workspace = tool["uv"]["workspace"]
        members = workspace.get("members")
        if not isinstance(members, list):
            return []
        return [member for member in members if isinstance(member, str)]
    else:
        return []


def initialize_workspace_context(
    root: WorkspaceRoot,
) -> Result[WorkspaceContext, AnalysisError]:
    toml_result = read_pyproject_toml(root.path / "pyproject.toml")
    if isinstance(toml_result, Failure):
        return toml_result

    toml_data = toml_result.unwrap()
    config_result = initialize_workspace_config(root.path, toml_data)
    if isinstance(config_result, Failure):
        return config_result

    if root.kind == WorkspaceRootKind.STANDALONE_PROJECT:
        project_config_result = analyze_project_config(
            project_root=root.path, toml_data=toml_data
        )
        if isinstance(project_config_result, Failure):
            return project_config_result
        return Success(
            WorkspaceContext(
                config=config_result.unwrap(),
                projects=tuple(
                    [
                        WorkspaceProject(
                            path=WorkspaceRelativePath(Path(".")),
                            config=project_config_result.unwrap(),
                        )
                    ]
                ),
            )
        )
    else:
        projects: list[WorkspaceProject] = []
        for member in get_uv_workspace_members(toml_data):
            project_root = root.path / member
            pyproject_path = project_root / "pyproject.toml"
            read_result = read_text(pyproject_path)
            if isinstance(read_result, Failure):
                return Failure(
                    AnalysisError(
                        "fail to read pyproject.toml",
                        file_path=pyproject_path,
                        phase="workspace-discovery",
                        context="gyomu_python_analysis.analysis.initialize.initialize_workspace_context",
                    ).chain(read_result.failure())
                )
            toml_data = loads(read_result.unwrap())
            project_relative_path = WorkspaceRelativePath(Path(member))
            project_config_result = analyze_project_config(
                project_root=project_root,
                toml_data=toml_data,
                project_relative_path=project_relative_path,
            )
            if isinstance(project_config_result, Failure):
                return project_config_result
            projects.append(
                WorkspaceProject(
                    path=project_relative_path,
                    config=project_config_result.unwrap(),
                )
            )
        return Success(
            WorkspaceContext(
                config=config_result.unwrap(),
                projects=tuple(projects),
            )
        )


# if __name__ == "__main__":
#     result = initialize_workspace_context(
#         WorkspaceRoot(
#             path=FullPath(Path("c:/data/program/python/gyomu-python")),
#             kind=WorkspaceRootKind.UV_WORKSPACE,
#         )
#     )
#     if isinstance(result, Success):
#         print(vars(result.unwrap()))
#     else:
#         failure = result.failure()
#         print(vars(failure))
