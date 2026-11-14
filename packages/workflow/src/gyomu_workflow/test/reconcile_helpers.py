from gyomu_infra.logger import logger
from gyomu_python_analysis.project.context import ProjectContext, WorkspaceProject
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_python_analysis.resolve.type_dump import dump_type
from gyomu_schema.schemas.testing.helper import HelperReconcileResult, HelperUpdate

from gyomu_workflow.test.helpers import _reconcile


def reconcile_helper_inventories(
    workspace_context: WorkspaceContext,
    workspace_project_context: WorkspaceProject,
    # additional_filename: str | None = None,
) -> None:

    reconcile_result, project_context = _reconcile(
        workspace_context=workspace_context,
        workspace_project_context=workspace_project_context,
    ).unwrap()

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
            expected_type = dump_type(
                target_expected.parameter_type,
                update.expected.target_identity.get_symbol_name(),
            )
            existing_type = dump_type(
                existing_param.parameter_type,
                update.existing.target_identity.get_symbol_name(),
            )
            if expected_type != existing_type:
                output += f"      - parameter: {existing_param.name} type difference\n"

                output += f"          - expected: {expected_type}\n"

                output += f"          - existing: {existing_type}\n"
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
