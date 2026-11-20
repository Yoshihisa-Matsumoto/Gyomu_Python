from pathlib import Path

from gyomu_config.manager import ConfigManager
from gyomu_python_analysis.analysis.initialize import (
    initialize_project_context,
)
from gyomu_python_analysis.project.context import ProjectContext, WorkspaceProject
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.protocols.interaction import InteractionExecutor
from gyomu_schema.schemas.config.test.model_defaults import (
    ModelDefault,
    ParameterDefault,
)
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.schemas.testing.helper import (
    HelperInventoryItem,
)
from gyomu_test.helper.defaults.requirements import (
    ConfiguredParameterDefault,
    MissingParameterDefault,
    ResolvedParameterDefault,
    is_supported_primitive_parameter_type,
    resolve_function_parameter_defaults,
)
from gyomu_test.helper.inventory.update_default import update_model_default
from returns.result import Failure, Result, Success

from gyomu_workflow.test.helpers._internal.direct import define_direct_parameter
from gyomu_workflow.test.helpers._internal.document import define_document_parameter
from gyomu_workflow.test.helpers._internal.error import wrap_gyomu_error
from gyomu_workflow.test.helpers._internal.reconcile import reconcile_package
from gyomu_workflow.test.helpers.models import (
    DefaultTypeParameterContext,
)


def update_helper_inventories(
    workspace_context: WorkspaceContext,
    workspace_project_context: WorkspaceProject,
    interaction: InteractionExecutor[str, Path],
) -> Result[None, GyomuError]:
    result = reconcile_package(
        workspace_context=workspace_context,
        workspace_project_context=workspace_project_context,
    )
    if isinstance(result, Failure):
        return result
    reconcile_result, project_context = result.unwrap()
    config_manager: ConfigManager = ConfigManager()
    if reconcile_result.create:
        create_result = _create_helper_inventory(
            create=reconcile_result.create,
            workspace_context=workspace_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )
        if isinstance(create_result, Failure):
            return create_result

    return Success(None)


def _create_helper_inventory(
    create: tuple[HelperInventoryItem, ...],
    workspace_context: WorkspaceContext,
    project_context: ProjectContext,
    config_manager: ConfigManager,
    interaction: InteractionExecutor[str, Path],
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
                lambda error: wrap_gyomu_error(
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
                root_context_result = initialize_project_context(
                    project_root=workspace_context.workspace_root.path,
                    source_root=ProjectRelativePath(Path(".")),
                )
                if isinstance(root_context_result, Failure):
                    return root_context_result.alt(
                        lambda error: wrap_gyomu_error(
                            error=error,
                            message="fail to initialize workspace root project context",
                        )
                    )
                parameter_context = DefaultTypeParameterContext(
                    parameter=parameter,
                    workspace_context=workspace_context,
                    project_context=project_context,
                    workspace_root_project_context=root_context_result.unwrap(),
                )
                if is_supported_primitive_parameter_type(parameter=parameter):
                    define_parameter_result = define_direct_parameter(
                        parameter_context=parameter_context, interaction=interaction
                    )

                else:
                    define_parameter_result = define_document_parameter(
                        parameter_context=parameter_context, interaction=interaction
                    )
                if isinstance(define_parameter_result, Failure):
                    return define_parameter_result
                resolved = define_parameter_result.unwrap()
                create_parameters.append(
                    ParameterDefault(
                        name=resolved.parameter.name,
                        value=resolved.default,
                    )
                )
        model_default: ModelDefault = ModelDefault(
            symbol_name=create_item.target_identity.get_symbol_name(),
            parameters=tuple(create_parameters),
        )
        update_result = update_model_default(
            project_context=project_context,
            target_identity=create_item.target_identity,
            model_default=model_default,
        )
        if isinstance(update_result, Failure):
            return update_result.alt(
                lambda error: wrap_gyomu_error(
                    error=error, message="fail to update function parameter"
                )
            )

    return Success(None)
