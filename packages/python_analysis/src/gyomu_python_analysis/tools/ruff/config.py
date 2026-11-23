from gyomu_schema.schemas.python.types import ProjectRelativePath

from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_python_analysis.tools.ruff.models import RuffCheckConfig


def for_file(
    workspace_relative_file_path: ProjectRelativePath,
    target_project_context: ProjectContext,
    workspace_root_project_context: ProjectContext,
    workspace_context: WorkspaceContext,
) -> RuffCheckConfig:
    del target_project_context, workspace_context

    return RuffCheckConfig(
        target=(
            workspace_root_project_context.project_root / workspace_relative_file_path
        ),
        working_directory=workspace_root_project_context.project_root,
    )


def for_project(
    target_project_context: ProjectContext,
    workspace_root_project_context: ProjectContext,
    workspace_context: WorkspaceContext,
) -> RuffCheckConfig:
    del workspace_context

    return RuffCheckConfig(
        target=target_project_context.project_root,
        working_directory=workspace_root_project_context.project_root,
    )


def for_workspace(
    workspace_context: WorkspaceContext,
) -> RuffCheckConfig:
    workspace_root = workspace_context.workspace_root

    return RuffCheckConfig(
        target=workspace_root.path,
        working_directory=workspace_root.path,
    )
