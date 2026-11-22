from pathlib import Path

from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.protocols.interaction import InteractionExecutor
from gyomu_schema.schemas.config.test.model_defaults import (
    Parameter,
)
from gyomu_test.helper.defaults.save import save_primitive_parameter_default_config
from returns.result import Failure, Result, Success

from gyomu_workflow.test.helpers._internal.error import wrap_gyomu_error
from gyomu_workflow.test.helpers._internal.models import (
    DefaultPrimitiveLiteralTypeConfigPlaceContext,
    DefaultPrimitiveLiteralTypeParameterContext,
)
from gyomu_workflow.test.helpers._internal.type_parameter_default import (
    build_primitive_default,
    has_primitive_type_parameter_default_config,
    select_config_place_to_save,
)


def configure_primitive_literal_type_parameter_default(
    parameter_context: DefaultPrimitiveLiteralTypeParameterContext,
    interaction: InteractionExecutor[str, Path],
    parameter: Parameter,
) -> Result[None, GyomuError]:

    predefined_exist_result = has_primitive_type_parameter_default_config(
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
                primitive_default=build_primitive_default(
                    parameter_type_name=parameter_context.parameter_type_name(),
                    missing=parameter_context.parameter,
                    parameter=parameter,
                ),
            ).alt(
                lambda error: wrap_gyomu_error(
                    error=error, message="fail to save type parameter"
                )
            )
    return Success(None)
