from pathlib import Path

from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_python_analysis.resolve.models import ReferencedType, SymbolType
from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.protocols.interaction import InteractionExecutor
from gyomu_schema.schemas.config.test.model_defaults import (
    Parameter,
    PrimitiveDefault,
    SymbolDefault,
)
from gyomu_schema.schemas.python.types import DeclarationIdentity
from gyomu_schema.schemas.testing.helper import ParameterInfo
from gyomu_test.helper.defaults.requirements import (
    MissingParameterDefault,
    resolve_primitive_parameter_type,
)
from gyomu_test.helper.defaults.save import (
    save_primitive_parameter_default_config,
    save_symbol_parameter_default_config,
)
from returns.result import Failure, Result, Success

from gyomu_workflow.interaction.confirm import simple_confirm
from gyomu_workflow.test.helpers._internal.error import wrap_gyomu_error
from gyomu_workflow.test.helpers._internal.models import (
    DefaultPrimitiveLiteralTypeConfigPlaceContext,
    DefaultPrimitiveLiteralTypeParameterContext,
    DefaultTypeParameterContext,
)
from gyomu_workflow.test.helpers._internal.type_parameter_default import (
    has_workspace_primitive_type_parameter_default_config,
    has_workspace_symbol_type_parameter_default_config,
    select_config_place_to_save,
)


def save_primitive_literal_type_parameter_default_in_workspace(
    parameter_context: DefaultPrimitiveLiteralTypeParameterContext, parameter: Parameter
) -> Result[None, GyomuError]:
    predefined_exist_result = has_workspace_primitive_type_parameter_default_config(
        parameter_context=parameter_context
    )
    if isinstance(predefined_exist_result, Failure):
        return predefined_exist_result
    exists = predefined_exist_result.unwrap()
    if not exists:
        return save_primitive_parameter_default_config(
            workspace_context=parameter_context.workspace_context,
            project_context=None,
            primitive_default=PrimitiveDefault(
                type_name=parameter_context.parameter_type_name(),
                parameter=parameter,
            ),
        ).alt(
            lambda error: wrap_gyomu_error(
                error=error, message="fail to save type parameter"
            )
        )
    return Success(None)


def configure_primitive_literal_type_parameter_default(
    parameter_context: DefaultPrimitiveLiteralTypeParameterContext,
    interaction: InteractionExecutor[str, Path],
    parameter: Parameter,
) -> Result[None, GyomuError]:

    predefined_exist_result = has_workspace_primitive_type_parameter_default_config(
        parameter_context=parameter_context
    )
    if isinstance(predefined_exist_result, Failure):
        return predefined_exist_result
    exists = predefined_exist_result.unwrap()
    if not exists:
        context = DefaultPrimitiveLiteralTypeConfigPlaceContext(
            parameter=parameter_context.parameter.parameter,
            resolved_type=parameter_context.resolved_type,
            workspace_context=parameter_context.workspace_context,
            test_project_context=parameter_context.project_context,
        )
        place_result = select_config_place_to_save(
            context=context,
            interaction=interaction,
        )
        if isinstance(place_result, Failure):
            return place_result
        place = place_result.unwrap()
        if place is not None:
            save_workspace, save_project = place

            return save_primitive_parameter_default_config(
                workspace_context=save_workspace,
                project_context=save_project,
                primitive_default=PrimitiveDefault(
                    type_name=parameter_context.parameter_type_name(),
                    parameter=parameter,
                ),
            ).alt(
                lambda error: wrap_gyomu_error(
                    error=error, message="fail to save type parameter"
                )
            )
    return Success(None)


def save_symbol_type_parameter_default_in_workspace(
    parameter_context: DefaultTypeParameterContext,
    parameter: Parameter,
    resolved_type: ReferencedType,
) -> Result[None, GyomuError]:
    predefined_exist_result = has_workspace_symbol_type_parameter_default_config(
        parameter_context=parameter_context, resolved_type=resolved_type
    )
    if isinstance(predefined_exist_result, Failure):
        return predefined_exist_result
    exists = predefined_exist_result.unwrap()
    if not exists:
        return save_symbol_parameter_default_config(
            workspace_context=parameter_context.workspace_context,
            project_context=None,
            module_path=parameter_context.model_identity.get_module_name(),
            symbol_default=SymbolDefault(
                symbol_name=parameter_context.model_identity.get_symbol_name(),
                parameter=parameter,
            ),
        ).alt(
            lambda error: wrap_gyomu_error(
                error=error, message="fail to save type parameter"
            )
        )
    return Success(None)


def configure_type_parameter_default(
    existing_parameter_default: Parameter,
    resolved_types: tuple[ReferencedType, ...],
    expected_parameter_info: ParameterInfo,
    workspace_context: WorkspaceContext,
    project_context: ProjectContext,
    interaction: InteractionExecutor[str, Path],
) -> Result[None, GyomuError]:
    confirm_result = simple_confirm(
        instruction=(
            "Do you want to save this parameter on the test project?\n"
            f"Project: {project_context.config.name}\n"
            f"Parameter: {expected_parameter_info.name}: "
            f"{expected_parameter_info.parameter_type.text}"
        ),
        interaction=interaction,
        initial_value=False,
    )
    if isinstance(confirm_result, Failure):
        return confirm_result
    confirmed_value = confirm_result.unwrap()
    if confirmed_value is None:
        return Failure(
            GyomuError(
                message="canceled the process",
                operation="helper",
                domain="test",
                reason="out_of_bounds",
            )
        )
    if confirmed_value:
        resolve_result = resolve_primitive_parameter_type(
            parameter=MissingParameterDefault(
                parameter=expected_parameter_info, missing_types=resolved_types
            )
        )
        if resolve_result is not None:
            parameter_type_name = resolve_result[0]

            return save_primitive_parameter_default_config(
                workspace_context=workspace_context,
                project_context=project_context,
                primitive_default=PrimitiveDefault(
                    type_name=parameter_type_name,
                    parameter=existing_parameter_default,
                ),
            ).alt(
                lambda error: wrap_gyomu_error(
                    error=error, message="fail to save primitive type parameter"
                )
            )
        else:
            target_type = resolved_types[0]
            if isinstance(target_type, SymbolType):
                identity = target_type.symbol.identity
            else:
                identity = DeclarationIdentity.create_from_symbol_id(
                    target_type.symbol_id
                )

            return save_symbol_parameter_default_config(
                workspace_context=workspace_context,
                project_context=project_context,
                module_path=identity.get_module_name(),
                symbol_default=SymbolDefault(
                    symbol_name=identity.get_symbol_name(),
                    parameter=existing_parameter_default,
                ),
            ).alt(
                lambda error: wrap_gyomu_error(
                    error=error, message="fail to save symbol type parameter"
                )
            )
    return Success(None)
