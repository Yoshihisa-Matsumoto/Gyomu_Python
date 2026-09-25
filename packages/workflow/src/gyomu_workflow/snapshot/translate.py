from os import getcwd
from pathlib import Path

from gyomu_infra.logger import logger
from gyomu_python_analysis.analysis.initialize import initialize_project_from_workspace
from gyomu_python_analysis.analysis.workspace import (
    find_root,
    initialize_workspace_context,
)
from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_python_analysis.project.workspace import WorkspaceRootKind
from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.schemas.types import FullPath
from returns.result import Failure, Result, Success

from gyomu_workflow.snapshot.models import SnapshotExecutionOption, SnapshotRequest


def translate_snapshot_request(
    project_name: str, option: SnapshotExecutionOption
) -> Result[SnapshotRequest, AnalysisError | GyomuError]:

    current_path = FullPath(Path(getcwd()))
    root_result = find_root(current_path)
    if isinstance(root_result, Failure):
        logger.error_object(root_result.failure())
        return root_result
    workspace = root_result.unwrap()
    assert workspace.kind == WorkspaceRootKind.UV_WORKSPACE
    workspace_result = initialize_workspace_context(workspace)
    if isinstance(workspace_result, Failure):
        logger.error_object(workspace_result.failure())
        return workspace_result
    workspace_context = workspace_result.unwrap()
    target_package = next(
        project
        for project in workspace_context.projects
        if project.config.name == project_name
    )
    if target_package is None:
        logger.error(f"{project_name} Not Found")
        return Failure(
            GyomuError(
                message="project not found",
                operation="package searc",
                domain="gyomu snapshot",
                reason="invalid_input",
            )
        )

    project_context = initialize_project_from_workspace(
        workspace_context.config, target_package
    )

    return Success(
        SnapshotRequest(
            repository_root_path=workspace.path,
            project_context=project_context,
            option=option,
        )
    )
