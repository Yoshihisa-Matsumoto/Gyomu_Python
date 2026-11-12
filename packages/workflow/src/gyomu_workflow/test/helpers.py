from pathlib import Path

from gyomu_config.manager import ConfigManager
from gyomu_python_analysis.analysis.initialize import (
    initialize_project_context,
    initialize_project_from_workspace,
)
from gyomu_python_analysis.project.context import ProjectContext, WorkspaceProject
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_schema.error.gyomu import GyomuError, GyomuErrorReason
from gyomu_schema.schemas.config.test.model_defaults import ParameterDefault
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.schemas.testing.helper import HelperInventoryItem
from gyomu_test.helper.defaults.requirements import (
    ConfiguredParameterDefault,
    MissingParameterDefault,
    ResolvedParameterDefault,
    resolve_function_parameter_defaults,
)
from gyomu_test.helper.inventory.existing import collect_existing_helper_inventory
from gyomu_test.helper.inventory.expected import collect_model_helper_inventory
from gyomu_test.helper.inventory.reconcile import reconcile
from returns.result import Failure, Result, Success


def _wrap_gyomu_error(
    error: BaseException, message: str, reason: GyomuErrorReason = "external_failure"
) -> GyomuError:
    return GyomuError(
        message=message,
        domain="Test Workflow",
        operation="Helper Inventories",
        reason="external_failure",
    ).chain(error)


def update_helper_inventories(
    workspace_context: WorkspaceContext,
    workspace_project_context: WorkspaceProject,
) -> Result[None, GyomuError]:
    project_context = initialize_project_from_workspace(
        workspace_path=workspace_context.workspace_root.path,
        project=workspace_project_context,
    )
    expected_result = collect_model_helper_inventory(project_context, workspace_context)

    if isinstance(expected_result, Failure):
        return expected_result.alt(
            lambda error: _wrap_gyomu_error(
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
            lambda error: _wrap_gyomu_error(
                error=error, message="fail to initialize project"
            )
        )

    existing_result = collect_existing_helper_inventory(
        root=root_context_result.unwrap(),
        target_project=project_context,
    )

    if isinstance(existing_result, Failure):
        return existing_result.alt(
            lambda error: _wrap_gyomu_error(
                error=error, message="fail to gather existing inventories"
            )
        )
    existing = existing_result.unwrap()

    reconcile_result = reconcile(existing=existing, expected=expected)
    config_manager: ConfigManager = ConfigManager()
    if reconcile_result.create:
        create_result = _create_helper_inventory(
            create=reconcile_result.create,
            workspace_context=workspace_context,
            project_context=project_context,
            config_manager=config_manager,
        )
        if isinstance(create_result, Failure):
            return create_result
    return Success(None)


def _create_helper_inventory(
    create: tuple[HelperInventoryItem, ...],
    workspace_context: WorkspaceContext,
    project_context: ProjectContext,
    config_manager: ConfigManager,
) -> Result[None, GyomuError]:
    for create_item in create:
        parameter_result = resolve_function_parameter_defaults(
            inventory=create_item,
            workspace_context=workspace_context,
            project_context=project_context,
            config_manager=config_manager,
        )
        if isinstance(parameter_result, Failure):
            return parameter_result.alt(
                lambda error: _wrap_gyomu_error(
                    error=error, message="fail to resolve function parameters"
                )
            )

        parameters = parameter_result.unwrap()
        create_parameters: list[ParameterDefault] = []
        for parameter in parameters:
            if isinstance(parameter, ConfiguredParameterDefault):
                create_parameters.append(
                    ParameterDefault(
                        name=parameter.parameter.name, value=parameter.parameter.default
                    )
                )
            elif isinstance(parameter, ResolvedParameterDefault):
                create_parameters.append(
                    ParameterDefault(
                        name=parameter.parameter.name, value=parameter.default
                    )
                )
            elif isinstance(parameter, MissingParameterDefault):
                print("test")

    return Success(None)


# def _define_parameter(
#     parameter: MissingParameterDefault,
#     workspace_root: WorkspaceRoot,
#     workspace_context: WorkspaceContext,
#     project_context: ProjectContext,
#     config_manager: ConfigManager,
# ) -> Result[ResolvedParameterDefault, GyomuError]: ...
