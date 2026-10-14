from gyomu_python_analysis.analysis.initialize import initialize_project_from_workspace
from gyomu_python_analysis.project.workspace import WorkspaceContext, WorkspaceProject

from gyomu_workflow.snapshot.models import SnapshotExecutionOption, SnapshotRequest


def translate_snapshot_request(
    workspace_context: WorkspaceContext,
    target_package: WorkspaceProject,
    option: SnapshotExecutionOption,
) -> SnapshotRequest:
    """Translate workspace and project context into a snapshot request.

    Args:
        workspace_context (WorkspaceContext): The workspace context containing the root
            path.
        target_package (WorkspaceProject): The target workspace project to snapshot.
        option (SnapshotExecutionOption): Options for executing the snapshot.

    Returns:
        SnapshotRequest: The generated snapshot request object.
    """

    project_context = initialize_project_from_workspace(
        workspace_context.path, target_package
    )

    return SnapshotRequest(
        repository_root_path=workspace_context.path,
        project_context=project_context,
        option=option,
        project=target_package,
        workspace=workspace_context,
    )
