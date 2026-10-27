from pathlib import Path

from gyomu_infra.logger import logger
from gyomu_python_analysis.analysis.initialize import (
    initialize_project_context,
    initialize_project_from_workspace,
)
from gyomu_python_analysis.project.context import ProjectContext, WorkspaceProject
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.schemas.testing.helper import HelperReconcileResult, HelperUpdate
from gyomu_test.helper.inventory.existing import collect_existing_helper_inventory
from gyomu_test.helper.inventory.expected import collect_model_helper_inventory
from gyomu_test.helper.inventory.reconcile import reconcile
from returns.result import Failure, Success


def reconcile_helper_inventories(
    workspace_context: WorkspaceContext,
    workspace_project_context: WorkspaceProject,
    additional_filename: str | None = None,
) -> None:
    project_context = initialize_project_from_workspace(
        workspace_path=workspace_context.path, project=workspace_project_context
    )
    expected_result = collect_model_helper_inventory(project_context, workspace_context)

    if isinstance(expected_result, Failure):
        logger.error_object(expected_result.failure(), depth=8)
    assert isinstance(expected_result, Success)
    expected = expected_result.unwrap()

    root_context_result = initialize_project_context(
        project_root=workspace_context.path,
        source_root=ProjectRelativePath(Path(".")),
    )
    assert isinstance(root_context_result, Success)

    existing_result = collect_existing_helper_inventory(
        root=root_context_result.unwrap(),
        target_project=project_context,
        files=(ProjectRelativePath(Path("test_support/helpers.py")),)
        if additional_filename is None
        else (
            ProjectRelativePath(Path("test_support/helpers.py")),
            ProjectRelativePath(Path(f"test_support/{additional_filename}.py")),
        ),
    )

    assert isinstance(existing_result, Success)
    existing = existing_result.unwrap()

    reconcile_result = reconcile(existing=existing, expected=expected)
    dump_reconcile_result(
        reconcile_result=reconcile_result, project_context=project_context
    )


def get_update_reconcile_result(update: HelperUpdate) -> str:
    output = ""
    for existing_param in update.existing.parameters:
        target_expected = next(
            (
                expected_item
                for expected_item in update.expected.parameters
                if expected_item.name == existing_param.name
            ),
            None,
        )
        if target_expected is None:
            output += f"      - parameter: {existing_param.name} only in existing\n"
        else:
            if target_expected.parameter_type != existing_param.parameter_type:
                output += f"      - parameter: {existing_param.name} type difference\n"
            if target_expected.default != existing_param.default:
                output += (
                    f"      - parameter: {existing_param.name} default difference\n"
                )

    for expected_param in update.expected.parameters:
        target_existing = next(
            (
                existing_item
                for existing_item in update.existing.parameters
                if existing_item.name == expected_param.name
            ),
            None,
        )
        if target_existing is None:
            output += f"      - parameter: {expected_param.name} only in expected\n"

    if output == "":
        for index, expected_param in enumerate(update.expected.parameters):
            existing_param = update.existing.parameters[index]
            if expected_param.name != existing_param.name:
                output += (
                    f"      - parameter: {expected_param.name} "
                    "is located differently in helper function\n"
                )
    if output == "":
        logger.error_object(update, depth=6)
    return output


def dump_reconcile_result(
    reconcile_result: HelperReconcileResult, project_context: ProjectContext
) -> None:
    create_statement = (
        (
            "CREATE\n"
            + "\n".join(
                [
                    ("  + " + created.target_identity.symbol_id)
                    for created in reconcile_result.create
                ]
            )
            + "\n\n"
        )
        if len(reconcile_result.create) > 0
        else ""
    )
    update_statement = (
        (
            "UPDATED\n"
            + "\n".join(
                [
                    (
                        f"  ~ {updated.existing.target_identity.symbol_id}\n"
                        f"    Helper:{updated.existing.function_name}\n"
                        "    Differences:\n"
                        f"{get_update_reconcile_result(updated)}\n"
                    )
                    for updated in reconcile_result.update
                ]
            )
            + "\n\n"
        )
        if len(reconcile_result.update) > 0
        else ""
    )
    unchanged_statement = (
        (
            "UNCHANGED\n"
            + "\n".join(
                [
                    ("  = " + unchanged.target_identity.symbol_id)
                    for unchanged in reconcile_result.unchanged
                ]
            )
            + "\n\n"
        )
        if len(reconcile_result.unchanged) > 0
        else ""
    )
    delete_statement = (
        (
            "DELETE CANDIDATES\n"
            + "\n".join(
                [
                    ("  - " + deleted.target_identity.symbol_id)
                    for deleted in reconcile_result.delete_candidates
                ]
            )
            + "\n\n"
        )
        if len(reconcile_result.delete_candidates) > 0
        else ""
    )
    print(
        "Helper Reconciliation\n"
        f"Project: {project_context.config.name}\n\n"
        "Summary\n"
        f"  Create:            {len(reconcile_result.create)}\n"
        f"  Update:            {len(reconcile_result.update)}\n"
        f"  Unchanged:         {len(reconcile_result.unchanged)}\n"
        f"  Delete candidate:  {len(reconcile_result.delete_candidates)}\n\n"
        f"{unchanged_statement}"
        f"{create_statement}"
        f"{update_statement}"
        f"{delete_statement}"
    )
