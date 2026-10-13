from gyomu_python_analysis.project.workspace import WorkspaceContext, WorkspaceProject
from gyomu_schema.error.gyomu import GyomuError
from returns.result import Failure, Result, Success


def find_project_by_name(
    workspace_context: WorkspaceContext, project_name: str
) -> Result[WorkspaceProject, GyomuError]:

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
