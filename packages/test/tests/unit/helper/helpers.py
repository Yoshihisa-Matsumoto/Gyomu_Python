from gyomu_python_analysis.analysis.initialize import initialize_project_from_workspace
from gyomu_python_analysis.analysis.workspace import (
    find_root,
    initialize_workspace_context,
)
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import (
    WorkspaceContext,
    WorkspaceRoot,
)
from gyomu_schema.schemas.types import FullPath
from returns.result import Success


def get_project_context(
    workspace_context: WorkspaceContext, project_name: str
) -> ProjectContext:
    project = next(
        (
            project
            for project in workspace_context.projects
            if project.config.name == project_name
        ),
        None,
    )
    assert project is not None
    return initialize_project_from_workspace(
        workspace_path=workspace_context.path, project=project
    )


def get_workspace_context(
    current_path: FullPath,
) -> tuple[WorkspaceRoot, WorkspaceContext]:

    root_result = find_root(current_path)
    assert isinstance(root_result, Success)
    workspace = root_result.unwrap()
    workspace_context_result = initialize_workspace_context(workspace)
    assert isinstance(workspace_context_result, Success)

    return workspace, workspace_context_result.unwrap()
