from gyomu_python_analysis.project.context import WorkspaceProject
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_schema.error.gyomu import GyomuError
from returns.result import Failure, Result, Success


def find_project_by_name(
    workspace_context: WorkspaceContext, project_name: str
) -> Result[WorkspaceProject, GyomuError]:
    """Finds a project by name within the workspace context.

    Args:
        workspace_context (WorkspaceContext): The workspace context containing projects
            to search.
        project_name (str): The name of the project to find.

    Returns:
        Result[WorkspaceProject, GyomuError]: A Result containing the WorkspaceProject
            if found, or a GyomuError if not found.
    """

    target_package = next(
        (
            project
            for project in workspace_context.projects
            if project.config.name == project_name
        ),
        None,
    )
    if target_package is None:
        return Failure(
            GyomuError(
                message="project not found",
                operation="package search",
                domain="gyomu snapshot",
                reason="invalid_input",
            )
        )
    return Success(target_package)
