from pathlib import Path

from gyomu_python_analysis.analysis.initialize import (
    initialize_project_context,
    initialize_project_from_workspace,
)
from gyomu_python_analysis.project.context import ProjectContext, WorkspaceProject
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.schemas.testing.helper import (
    HelperReconcileResult,
)
from gyomu_test.helper.inventory.existing import collect_existing_helper_inventory
from gyomu_test.helper.inventory.expected import collect_model_helper_inventory
from gyomu_test.helper.inventory.reconcile import reconcile
from returns.result import Failure, Result, Success

from gyomu_workflow.test.helpers._internal.error import wrap_gyomu_error


def reconcile_package(
    workspace_context: WorkspaceContext,
    workspace_project_context: WorkspaceProject,
) -> Result[tuple[HelperReconcileResult, ProjectContext], GyomuError]:
    project_context = initialize_project_from_workspace(
        workspace_path=workspace_context.workspace_root.path,
        project=workspace_project_context,
    )
    expected_result = collect_model_helper_inventory(project_context, workspace_context)

    if isinstance(expected_result, Failure):
        return expected_result.alt(
            lambda error: wrap_gyomu_error(
                error=error, message="fail to collect inventories from models"
            )
        )
    expected = expected_result.unwrap()

    root_context_result = initialize_project_context(
        project_root=workspace_context.workspace_root.path,
        source_root=ProjectRelativePath(Path(".")),
    )
    if isinstance(root_context_result, Failure):
        return root_context_result.alt(
            lambda error: wrap_gyomu_error(
                error=error, message="fail to initialize project"
            )
        )

    existing_result = collect_existing_helper_inventory(
        root=root_context_result.unwrap(),
        target_project=project_context,
    )

    if isinstance(existing_result, Failure):
        return existing_result.alt(
            lambda error: wrap_gyomu_error(
                error=error, message="fail to gather existing inventories"
            )
        )
    existing = existing_result.unwrap()

    return Success((reconcile(existing=existing, expected=expected), project_context))
