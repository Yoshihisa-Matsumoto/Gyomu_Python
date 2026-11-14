from dataclasses import dataclass
from pathlib import Path

from gyomu_config.manager import ConfigManager
from gyomu_python_analysis.analysis.initialize import (
    initialize_project_context,
    initialize_project_from_workspace,
)
from gyomu_python_analysis.project.context import ProjectContext, WorkspaceProject
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_schema.error.gyomu import GyomuError, GyomuErrorReason
from gyomu_schema.error.validation import ValidationError
from gyomu_schema.protocols.interaction import InteractionExecutor
from gyomu_schema.schemas.config.test.model_defaults import (
    LiteralParameter,
    ModelDefault,
    Parameter,
    ParameterDefault,
)
from gyomu_schema.schemas.interaction.request import (
    InputMode,
    InteractionDirectRequest,
    InteractionRequest,
)
from gyomu_schema.schemas.interaction.result import (
    InteractionCancelled,
    InteractionRejected,
)
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.schemas.testing.helper import (
    HelperInventoryItem,
    HelperReconcileResult,
)
from gyomu_test.helper.defaults.requirements import (
    ConfiguredParameterDefault,
    MissingParameterDefault,
    ResolvedParameterDefault,
    get_primitive_type_name,
    is_supported_primitive_parameter_type,
    resolve_function_parameter_defaults,
)
from gyomu_test.helper.inventory.existing import collect_existing_helper_inventory
from gyomu_test.helper.inventory.expected import collect_model_helper_inventory
from gyomu_test.helper.inventory.reconcile import reconcile
from gyomu_test.helper.inventory.update_default import update_model_default
from returns.result import Failure, Result, Success


def _wrap_gyomu_error(
    error: BaseException, message: str, reason: GyomuErrorReason = "external_failure"
) -> GyomuError:
    return GyomuError(
        message=message,
        domain="Test Workflow",
        operation="Helper Inventories",
        reason=reason,
    ).chain(error)


def _reconcile(
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

    return Success((reconcile(existing=existing, expected=expected), project_context))


def update_helper_inventories(
    workspace_context: WorkspaceContext,
    workspace_project_context: WorkspaceProject,
    interaction: InteractionExecutor,
) -> Result[None, GyomuError]:
    result = _reconcile(
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
    interaction: InteractionExecutor,
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
                parameter_context = DefaultTypeParameterContext(
                    parameter=parameter,
                    workspace_context=workspace_context,
                    project_context=project_context,
                )
                define_parameter_result = _define_parameter(
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
                lambda error: _wrap_gyomu_error(
                    error=error, message="fail to update function parameter"
                )
            )

    return Success(None)


@dataclass(frozen=True)
class DefaultTypeParameterContext:
    parameter: MissingParameterDefault
    workspace_context: WorkspaceContext
    project_context: ProjectContext


class PrimitiveValueCodec:
    def parse(
        self, raw_input: str, context: DefaultTypeParameterContext
    ) -> Result[LiteralParameter, ValidationError]:
        parameter_type = get_primitive_type_name(context.parameter)
        try:
            match parameter_type:
                case "str":
                    return Success(LiteralParameter(value=raw_input))
                case "int":
                    return Success(LiteralParameter(value=int(raw_input)))
                case "bool":
                    match raw_input.strip().lower():
                        case "true":
                            return Success(LiteralParameter(value=True))
                        case "false":
                            return Success(LiteralParameter(value=False))
                        case _:
                            return Failure(
                                ValidationError(
                                    "Invalid value; enter true or false.",
                                    input=raw_input,
                                )
                            )
                case "float":
                    return Success(LiteralParameter(value=float(raw_input)))
            return Failure(ValidationError(f"Unsupported Type: {parameter_type}"))
        except ValueError as e:
            return Failure(
                ValidationError(
                    f"fail to convert into type={parameter_type}", input=raw_input
                ).chain(e)
            )


def _build_interaction_request(
    parameter_context: DefaultTypeParameterContext,
) -> Result[
    InteractionRequest[str, DefaultTypeParameterContext, Parameter], GyomuError
]:
    if is_supported_primitive_parameter_type(parameter=parameter_context.parameter):
        return Success(
            InteractionDirectRequest[str, DefaultTypeParameterContext, Parameter](
                instruction="Please define your type parameter for ",
                context=parameter_context,
                input_mode=InputMode.DIRECT,
                codec=PrimitiveValueCodec(),
            )
        )
    return Failure(
        GyomuError(
            "unsupported", operation="test", domain="test", reason="out_of_bounds"
        )
    )


def _define_parameter(
    parameter_context: DefaultTypeParameterContext,
    interaction: InteractionExecutor,
) -> Result[ResolvedParameterDefault, GyomuError]:
    request_result = _build_interaction_request(parameter_context=parameter_context)
    if isinstance(request_result, Failure):
        return request_result
    request = request_result.unwrap()
    interaction_result = interaction.execute(request=request)
    if isinstance(interaction_result, Failure):
        return interaction_result
    result = interaction_result.unwrap()
    if isinstance(result, InteractionRejected | InteractionCancelled):
        return Failure(
            GyomuError(
                "parameter was not defined by user",
                operation="test",
                domain="test",
                reason="external_failure",
            )
        )
    return Success(
        ResolvedParameterDefault(
            parameter=parameter_context.parameter.parameter, default=result.value
        )
    )
