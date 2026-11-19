from pathlib import Path

from gyomu_schema.schemas.python.types import ProjectRelativePath
from returns.result import Result

from gyomu_python_analysis.error.tools import ToolConfigError
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_python_analysis.tools.mypy.models import MypyCheckConfig, MypyTarget


def for_file(
    file_path: ProjectRelativePath,
    project_context: ProjectContext,
    root_project_context: ProjectContext,
    workspace_context: WorkspaceContext,
) -> MypyCheckConfig:
    return MypyCheckConfig(
        targets=(file_path,),
        config_file=None,
        cache_dir=None,
        explicit_package_bases=True,
        working_directory=root_project_context.project_root,
        mypy_path=_gather_workspace_projects_src_path(
            project_context=project_context, workspace_context=workspace_context
        ),
    )


def for_project(
    project_context: ProjectContext,
    target: MypyTarget,
) -> Result[MypyCheckConfig, ToolConfigError]: ...


def for_workspace(
    workspace_context: WorkspaceContext,
    target: MypyTarget,
) -> Result[MypyCheckConfig, ToolConfigError]: ...


def _gather_workspace_projects_src_path(
    project_context: ProjectContext,
    workspace_context: WorkspaceContext,
) -> tuple[Path, ...]:
    target_paths: list[Path] = []

    target_paths.append(project_context.project_root / project_context.source_root)

    dependencies = project_context.config.get_attribute(
        "project.dependencies", list[str]
    )
    if dependencies is not None:
        for dependency in dependencies:
            dependency_context = workspace_context.get_project_context(dependency)
            if dependency_context is not None:
                target_paths.append(
                    dependency_context.project_root / dependency_context.source_root
                )

    return tuple(target_paths)
