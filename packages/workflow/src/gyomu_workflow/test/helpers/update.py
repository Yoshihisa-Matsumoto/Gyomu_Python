from pathlib import Path

from gyomu_config.manager import ConfigManager
from gyomu_infra.logger import logger
from gyomu_python_analysis.project.context import ProjectContext, WorkspaceProject
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_python_analysis.resolve.models import ReferencedType
from gyomu_python_analysis.tools.mypy.check import check_file
from gyomu_python_analysis.tools.ruff.check import (
    check_file_lint,
    format_file,
)
from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.protocols.interaction import InteractionExecutor
from gyomu_schema.schemas.config.test.model_defaults import (
    ModelDefault,
    Parameter,
    ParameterDefault,
)
from gyomu_schema.schemas.python.module import ModuleAnalysis
from gyomu_schema.schemas.python.types import WorkspaceRelativePath
from gyomu_schema.schemas.testing.helper import (
    HelperInventoryItem,
    HelperUpdate,
    ParameterInfo,
)
from gyomu_test.helper.defaults.referenced_types import deduplicate_referenced_types
from gyomu_test.helper.defaults.requirements import (
    ConfiguredParameterDefault,
    MissingParameterDefault,
    ResolvedParameterDefault,
    is_supported_primitive_parameter_type,
    resolve_function_parameter_default,
    resolve_primitive_parameter_type,
)
from gyomu_test.helper.inventory.config import get_helper_file_paths
from gyomu_test.helper.inventory.update import update_helper_file
from gyomu_test.helper.inventory.update_default import update_model_default
from returns.result import Failure, Result, Success

from gyomu_workflow.test.helpers._internal.direct import define_direct_parameter
from gyomu_workflow.test.helpers._internal.document import define_document_parameter
from gyomu_workflow.test.helpers._internal.error import wrap_gyomu_error
from gyomu_workflow.test.helpers._internal.models import (
    DefaultPrimitiveLiteralTypeParameterContext,
    DefaultTypeParameterContext,
)
from gyomu_workflow.test.helpers._internal.reconcile import reconcile_package
from gyomu_workflow.test.helpers._internal.type_parameter_config import (
    configure_type_parameter_default,
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
    # print(format_object(reconcile_result, depth=8))
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

    if reconcile_result.delete_candidates:
        for item in reconcile_result.delete_candidates:
            logger.warning(
                message=(
                    f"{item.function_name} for {item.target_identity.symbol_id} "
                    "is not appropriate candiate. Please check"
                )
            )
    if reconcile_result.update:
        update_result = _update_helper_inventory(
            update=reconcile_result.update,
            workspace_context=workspace_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )
        if isinstance(update_result, Failure):
            return update_result

    if reconcile_result.create or reconcile_result.update:
        helper_file_path_result = get_helper_file_paths(
            project_context=project_context, existing_only=True
        )
        if isinstance(helper_file_path_result, Failure):
            return helper_file_path_result.alt(
                lambda error: wrap_gyomu_error(
                    error=error, message="fail to enumerate helper file path list"
                )
            )
        for helper_file_path in helper_file_path_result.unwrap():
            helper_file_workspace_relative_path = WorkspaceRelativePath(
                (project_context.project_root / helper_file_path).relative_to(
                    workspace_context.workspace_root.path
                )
            )
            validate_result = _validate_helper_file(
                helper_file_path=helper_file_workspace_relative_path,
                workspace_context=workspace_context,
                project_context=project_context,
            )
            if isinstance(validate_result, Failure):
                return validate_result

    return Success(None)


def _should_save_existing_parameter_as_type_default(
    existing_parameter_default: Parameter | None,
    parameter: ConfiguredParameterDefault
    | ResolvedParameterDefault
    | MissingParameterDefault,
) -> bool:
    if existing_parameter_default is None:
        return False
    if isinstance(parameter, ConfiguredParameterDefault):
        return existing_parameter_default != parameter.parameter.default
    elif isinstance(parameter, ResolvedParameterDefault):
        return existing_parameter_default != parameter.default
    else:
        return True


def _define_helper_inventory_parameter(
    inventory: HelperInventoryItem,
    module_analysis: ModuleAnalysis,
    parameter_info: ParameterInfo,
    workspace_context: WorkspaceContext,
    project_context: ProjectContext,
    config_manager: ConfigManager,
    interaction: InteractionExecutor[str, Path],
    existing_parameter_info: ParameterInfo | None,
) -> Result[tuple[ParameterDefault, tuple[ReferencedType, ...]], GyomuError]:
    parameter_result = resolve_function_parameter_default(
        inventory=inventory,
        parameter_info=parameter_info,
        module_analysis=module_analysis,
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
    parameter, resolved_types = parameter_result.unwrap()
    # print(type(parameter).__name__)
    # print(format_object(parameter, depth=8))
    # print(f"resolve_function_parameter_default resolved_types: {len(resolved_types)}")

    existing_parameter_default = (
        existing_parameter_info.default if existing_parameter_info is not None else None
    )
    if (
        _should_save_existing_parameter_as_type_default(
            existing_parameter_default=existing_parameter_default, parameter=parameter
        )
        and existing_parameter_default is not None
    ):
        save_parameter_result = configure_type_parameter_default(
            existing_parameter_default=existing_parameter_default,
            resolved_types=resolved_types,
            expected_parameter_info=parameter_info,
            workspace_context=workspace_context,
            project_context=project_context,
            interaction=interaction,
        )
        if isinstance(save_parameter_result, Failure):
            return save_parameter_result

    if isinstance(parameter, ConfiguredParameterDefault):
        return Success(
            (
                ParameterDefault(
                    name=parameter.parameter.name,
                    value=existing_parameter_default
                    if existing_parameter_default is not None
                    else parameter.parameter.default,
                ),
                resolved_types,
            )
        )
    elif isinstance(parameter, ResolvedParameterDefault):
        return Success(
            (
                ParameterDefault(
                    name=parameter.parameter.name,
                    value=existing_parameter_default
                    if existing_parameter_default is not None
                    else parameter.default,
                ),
                resolved_types,
            )
        )
    else:
        parameter_context = DefaultTypeParameterContext(
            model_identity=inventory.target_identity,
            parameter=parameter,
            workspace_context=workspace_context,
            project_context=project_context,
            config_manager=config_manager,
        )
        resolve_result = resolve_primitive_parameter_type(parameter=parameter)
        # print(format_object(resolve_result, depth=8))
        if existing_parameter_default is None:
            if resolve_result is not None:
                parameter_context = DefaultPrimitiveLiteralTypeParameterContext(
                    model_identity=inventory.target_identity,
                    parameter=parameter,
                    workspace_context=workspace_context,
                    project_context=project_context,
                    config_manager=config_manager,
                    resolved_type=resolve_result[1],
                )
                if is_supported_primitive_parameter_type(
                    parameter_type_name=resolve_result[0],
                ):
                    define_parameter_result = define_direct_parameter(
                        parameter_context=parameter_context,
                        interaction=interaction,
                    )
                else:
                    define_parameter_result = define_document_parameter(
                        parameter_context=parameter_context, interaction=interaction
                    )
            else:
                define_parameter_result = define_document_parameter(
                    parameter_context=parameter_context, interaction=interaction
                )
            if isinstance(define_parameter_result, Failure):
                return define_parameter_result
            resolved = define_parameter_result.unwrap()
            return Success(
                (
                    ParameterDefault(
                        name=resolved.parameter.name,
                        value=resolved.default,
                    ),
                    resolved_types,
                )
            )
        else:
            return Success(
                (
                    ParameterDefault(
                        name=parameter.parameter.name,
                        value=existing_parameter_default,
                    ),
                    resolved_types,
                )
            )


def _resolve_helper_inventory_item(
    expected_item: HelperInventoryItem,
    workspace_context: WorkspaceContext,
    project_context: ProjectContext,
    config_manager: ConfigManager,
    interaction: InteractionExecutor[str, Path],
    existing_item: HelperInventoryItem | None,
) -> Result[tuple[ModelDefault, tuple[ReferencedType, ...]], GyomuError]:
    cache_result = workspace_context.find_file_analysis_context(
        target_identity=expected_item.target_identity
    )
    if isinstance(cache_result, Failure):
        return cache_result.alt(
            lambda error: wrap_gyomu_error(
                error=error, message="fail to get file analysis"
            )
        )
    search_result = cache_result.unwrap()
    if search_result is None:
        return Failure(
            GyomuError(
                "file analysis is not found",
                operation="create helper inventory",
                domain="test",
                reason="unexpected",
            )
        )
    module_analysis = search_result[0].analysis

    create_parameters: list[ParameterDefault] = []
    referenced_types: list[ReferencedType] = []

    for parameter_info in expected_item.parameters:
        existing_parameter_info = (
            next(
                (
                    item
                    for item in existing_item.parameters
                    if item.name == parameter_info.name
                    and item.parameter_type.text == parameter_info.parameter_type.text
                ),
                None,
            )
            if existing_item is not None
            else None
        )
        # print(f"{parameter_info.name}: {parameter_info.parameter_type.text}")
        parameter_result = _define_helper_inventory_parameter(
            inventory=expected_item,
            module_analysis=module_analysis,
            parameter_info=parameter_info,
            workspace_context=workspace_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
            existing_parameter_info=existing_parameter_info,
        )
        if isinstance(parameter_result, Failure):
            return parameter_result
        parameter, ref_type = parameter_result.unwrap()
        create_parameters.append(parameter)
        # print(f"ref_type count: {len(ref_type)}")
        # for ref in ref_type:
        #     print(
        #         ref.symbol.identity.symbol_id
        #         if isinstance(ref, SymbolType)
        #         else ref.symbol_id
        #     )
        referenced_types.extend(ref_type)
    model_default: ModelDefault = ModelDefault(
        symbol_name=expected_item.target_identity.get_symbol_name(),
        parameters=tuple(create_parameters),
    )
    update_result = update_model_default(
        project_context=project_context,
        target_identity=expected_item.target_identity,
        model_default=model_default,
    )
    if isinstance(update_result, Failure):
        return update_result.alt(
            lambda error: wrap_gyomu_error(
                error=error, message="fail to update function parameter"
            )
        )
    # print(format_object(referenced_types, depth=8))
    unique_ref_types = deduplicate_referenced_types(referenced_types=referenced_types)

    return Success((model_default, unique_ref_types))


def _validate_helper_file(
    helper_file_path: WorkspaceRelativePath,
    workspace_context: WorkspaceContext,
    project_context: ProjectContext,
) -> Result[None, GyomuError]:

    # run mypy validation
    check_mypy_result = check_file(
        workspace_relative_file_path=helper_file_path,
        target_project_context=project_context,
        workspace_context=workspace_context,
    )
    if isinstance(check_mypy_result, Failure):
        return check_mypy_result.alt(
            lambda error: wrap_gyomu_error(
                error=error, message="mypy check fail on file"
            )
        )
    mypy_result = check_mypy_result.unwrap()
    if not mypy_result.success:
        return Failure(
            GyomuError(
                message="mypy validation error",
                operation="inventory",
                domain="test",
                reason="external_failure",
                details={"validation": mypy_result.diagnostics},
            )
        )

    # run ruff validation

    check_ruff_lint_result = check_file_lint(
        workspace_relative_file_path=helper_file_path,
        workspace_context=workspace_context,
    )
    if isinstance(check_ruff_lint_result, Failure):
        return check_ruff_lint_result.alt(
            lambda error: wrap_gyomu_error(
                error=error, message="ruff format lint fail on file"
            )
        )
    ruff_result = check_ruff_lint_result.unwrap()
    if not ruff_result.success:
        return Failure(
            GyomuError(
                message="ruff lint validation error",
                operation="inventory",
                domain="test",
                reason="external_failure",
                details={"validation": ruff_result.diagnostics},
            )
        )
    return Success(None)


def _resolve_and_update_helper_inventory_item(
    expected_item: HelperInventoryItem,
    existing_item: HelperInventoryItem | None,
    resolve_existing_item: HelperInventoryItem | None,
    workspace_context: WorkspaceContext,
    project_context: ProjectContext,
    config_manager: ConfigManager,
    interaction: InteractionExecutor[str, Path],
) -> Result[None, GyomuError]:
    resolve_result = _resolve_helper_inventory_item(
        expected_item=expected_item,
        workspace_context=workspace_context,
        project_context=project_context,
        config_manager=config_manager,
        interaction=interaction,
        existing_item=resolve_existing_item,
    )
    if isinstance(resolve_result, Failure):
        return resolve_result
    model_default, referenced_types = resolve_result.unwrap()
    # print(format_object(referenced_types, depth=5))
    update_file_result = update_helper_file(
        expected_item=expected_item,
        workspace_context=workspace_context,
        project_context=project_context,
        model_default=model_default,
        referenced_types=referenced_types,
        existing_item=existing_item,
    )
    if isinstance(update_file_result, Failure):
        return update_file_result.alt(
            lambda error: wrap_gyomu_error(
                error=error, message="fail to update helper file"
            )
        )
    helper_file_path = update_file_result.unwrap()

    format_result = format_file(
        workspace_relative_file_path=helper_file_path,
        workspace_context=workspace_context,
    )
    if isinstance(format_result, Failure):
        return format_result.alt(
            lambda error: wrap_gyomu_error(error=error, message="fail to format file")
        )
    return Success(None)
    # return _validate_helper_file(
    #     helper_file_path=helper_file_path,
    #     workspace_context=workspace_context,
    #     project_context=project_context,
    # )


def _create_helper_inventory_item(
    expected_item: HelperInventoryItem,
    workspace_context: WorkspaceContext,
    project_context: ProjectContext,
    config_manager: ConfigManager,
    interaction: InteractionExecutor[str, Path],
) -> Result[None, GyomuError]:
    return _resolve_and_update_helper_inventory_item(
        expected_item=expected_item,
        existing_item=None,
        resolve_existing_item=None,
        workspace_context=workspace_context,
        project_context=project_context,
        config_manager=config_manager,
        interaction=interaction,
    )


def _create_helper_inventory(
    create: tuple[HelperInventoryItem, ...],
    workspace_context: WorkspaceContext,
    project_context: ProjectContext,
    config_manager: ConfigManager,
    interaction: InteractionExecutor[str, Path],
) -> Result[None, GyomuError]:
    for create_item in create:
        item_result = _create_helper_inventory_item(
            expected_item=create_item,
            workspace_context=workspace_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )
        if isinstance(item_result, Failure):
            return item_result

    return Success(None)


def _update_helper_inventory_item(
    item: HelperUpdate,
    workspace_context: WorkspaceContext,
    project_context: ProjectContext,
    config_manager: ConfigManager,
    interaction: InteractionExecutor[str, Path],
) -> Result[None, GyomuError]:
    resolve_existing_item = (
        None
        if item.existing.function_name != item.expected.function_name
        else item.existing
    )

    return _resolve_and_update_helper_inventory_item(
        expected_item=item.expected,
        existing_item=item.existing,
        resolve_existing_item=resolve_existing_item,
        workspace_context=workspace_context,
        project_context=project_context,
        config_manager=config_manager,
        interaction=interaction,
    )


def _update_helper_inventory(
    update: tuple[HelperUpdate, ...],
    workspace_context: WorkspaceContext,
    project_context: ProjectContext,
    config_manager: ConfigManager,
    interaction: InteractionExecutor[str, Path],
) -> Result[None, GyomuError]:
    for update_item in update:
        print(f"--Update: {update_item.existing.function_name}")
        item_result = _update_helper_inventory_item(
            item=update_item,
            workspace_context=workspace_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )
        if isinstance(item_result, Failure):
            return item_result

    return Success(None)
