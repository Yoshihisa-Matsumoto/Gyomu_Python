from pathlib import Path

from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_python_analysis.resolve.models import ReferencedType
from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.protocols.interaction import InteractionExecutor
from gyomu_schema.schemas.interaction.request import (
    InteractionRequest,
    InteractionSelectRequest,
    SelectionOption,
)
from gyomu_schema.schemas.interaction.result import InteractionCancelled
from gyomu_test.helper.defaults.load import (
    load_workspace_primitive_parameter_default_config,
    load_workspace_symbol_parameter_default_config,
)
from gyomu_test.helper.defaults.resolution import (
    PrimitiveDefaultConfigContext,
    SymbolDefaultConfigContext,
)
from returns.result import Failure, Result, Success

from gyomu_workflow.test.helpers._internal.error import wrap_gyomu_error
from gyomu_workflow.test.helpers._internal.models import (
    DefaultPrimitiveLiteralTypeConfigPlaceContext,
    DefaultPrimitiveLiteralTypeParameterContext,
    DefaultTypeConfigPlaceContext,
    DefaultTypeParameterContext,
)


class ConfigPlaceSelectionProvider:
    def create_selections(
        self, context: DefaultTypeConfigPlaceContext
    ) -> Result[
        tuple[SelectionOption[WorkspaceContext | ProjectContext], ...], GyomuError
    ]:
        selections: list[SelectionOption[WorkspaceContext | ProjectContext]] = []

        selections.append(
            SelectionOption[WorkspaceContext | ProjectContext](
                label="Workspace Root", value=context.workspace_context
            )
        )
        selections.append(
            SelectionOption[WorkspaceContext | ProjectContext](
                label=f"Test Project: {context.test_project_context.config.name}",
                value=context.test_project_context,
            )
        )
        if (
            not isinstance(context, DefaultPrimitiveLiteralTypeConfigPlaceContext)
            and context.model_project_context is not None
        ):
            selections.append(
                SelectionOption[WorkspaceContext | ProjectContext](
                    label=f"Model Project: {context.model_project_context.config.name}",
                    value=context.model_project_context,
                )
            )
        return Success(tuple(selections))


def _build_config_place_selection_request(
    context: DefaultTypeConfigPlaceContext,
) -> InteractionRequest[
    str,
    Path,
    DefaultTypeConfigPlaceContext,
    WorkspaceContext | ProjectContext,
]:
    return InteractionSelectRequest[
        DefaultTypeConfigPlaceContext, WorkspaceContext | ProjectContext
    ](
        instruction=(
            "Please choose where to save for "
            f"{context.parameter.name}:"
            f"{context.parameter.parameter_type.text}"
        ),
        context=context,
        selection_provider=ConfigPlaceSelectionProvider(),
    )


def select_config_place_to_save(
    context: DefaultTypeConfigPlaceContext,
    interaction: InteractionExecutor[str, Path],
) -> Result[tuple[WorkspaceContext, ProjectContext | None] | None, GyomuError]:
    request = _build_config_place_selection_request(context)
    interaction_result = interaction.execute(request=request)
    if isinstance(interaction_result, Failure):
        return interaction_result
    reaction = interaction_result.unwrap()
    if isinstance(reaction, InteractionCancelled):
        return Success(None)
    project_context = (
        reaction.value if isinstance(reaction.value, ProjectContext) else None
    )
    return Success((context.workspace_context, project_context))


def has_workspace_primitive_type_parameter_default_config(
    parameter_context: DefaultPrimitiveLiteralTypeParameterContext,
) -> Result[bool, GyomuError]:

    primitive_literal = parameter_context.resolved_type
    primitive_context: PrimitiveDefaultConfigContext = PrimitiveDefaultConfigContext(
        type_default=primitive_literal,
        workspace_context=parameter_context.workspace_context,
        project_context=parameter_context.project_context,
    )
    load_result = load_workspace_primitive_parameter_default_config(
        context=primitive_context, config_manager=parameter_context.config_manager
    )
    if isinstance(load_result, Failure):
        return load_result.alt(
            lambda error: wrap_gyomu_error(
                error=error, message="fail to load type parameter"
            )
        )
    return Success(load_result.unwrap() is not None)


def has_workspace_symbol_type_parameter_default_config(
    parameter_context: DefaultTypeParameterContext, resolved_type: ReferencedType
) -> Result[bool, GyomuError]:

    symbol_context: SymbolDefaultConfigContext = SymbolDefaultConfigContext(
        type_default=resolved_type,
        workspace_context=parameter_context.workspace_context,
        project_context=parameter_context.project_context,
    )
    load_result = load_workspace_symbol_parameter_default_config(
        context=symbol_context, config_manager=parameter_context.config_manager
    )
    if isinstance(load_result, Failure):
        return load_result.alt(
            lambda error: wrap_gyomu_error(
                error=error, message="fail to load type parameter"
            )
        )
    return Success(load_result.unwrap() is not None)
