from pathlib import Path

from gyomu_python_analysis.analysis.initialize import (
    initialize_project_from_workspace,
)
from gyomu_python_analysis.project.context import WorkspaceProject
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_test.helper.inventory.migration import migrate


def migrate_default_from_existing_helpers(
    workspace_context: WorkspaceContext,
    workspace_project_context: WorkspaceProject,
    additional_filename: str | None = None,
) -> None:
    project_context = initialize_project_from_workspace(
        workspace_path=workspace_context.path, project=workspace_project_context
    )
    migrate(
        workspace_context=workspace_context,
        project_context=project_context,
        helper_files=(ProjectRelativePath(Path("test_support/helpers.py")),)
        if additional_filename is None
        else (
            ProjectRelativePath(Path("test_support/helpers.py")),
            ProjectRelativePath(Path(f"test_support/{additional_filename}.py")),
        ),
    )
