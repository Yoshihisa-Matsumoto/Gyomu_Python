from pathlib import Path

from gyomu_config.manager import ConfigManager
from gyomu_infra.filesystem.file_io import write_text
from gyomu_python_analysis.analysis.initialize import (
    initialize_project_context,
)
from gyomu_python_analysis.analysis.load_file_context import load_file_analysis_context
from gyomu_python_analysis.project.context import ProjectContext, WorkspaceProject
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_python_analysis.resolve.models import ReferencedType
from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.protocols.interaction import InteractionExecutor
from gyomu_schema.schemas.config.test.model_defaults import (
    ModelDefault,
    ParameterDefault,
)
from gyomu_schema.schemas.python.file_analysis import FileAnalysisContext
from gyomu_schema.schemas.python.module import ModuleAnalysis
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.schemas.testing.helper import (
    HelperInventoryItem,
    ParameterInfo,
)
from gyomu_test.helper.defaults.referenced_types import deduplicate_referenced_types
from gyomu_test.helper.defaults.requirements import (
    ConfiguredParameterDefault,
    ResolvedParameterDefault,
    is_supported_primitive_parameter_type,
    resolve_function_parameter_default,
    resolve_primitive_parameter_type,
)
from gyomu_test.helper.inventory.config import get_helper_file_path
from gyomu_test.helper.inventory.expected import reflect_updated_inventory
from gyomu_test.helper.inventory.function import (
    generate_function_code_lines,
    generate_import_code_lines,
)
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
    workspace_root_project_context = root_context_result.unwrap()
    if reconcile_result.create:
        create_result = _create_helper_inventory(
            create=reconcile_result.create,
            workspace_context=workspace_context,
            workspace_root_project_context=workspace_root_project_context,
            project_context=project_context,
            config_manager=config_manager,
            interaction=interaction,
        )
        if isinstance(create_result, Failure):
            return create_result

    return Success(None)


def _define_helper_inventory_parameter(
    inventory: HelperInventoryItem,
    module_analysis: ModuleAnalysis,
    parameter_info: ParameterInfo,
    workspace_context: WorkspaceContext,
    workspace_root_project_context: ProjectContext,
    project_context: ProjectContext,
    config_manager: ConfigManager,
    interaction: InteractionExecutor[str, Path],
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
    parameter = parameter_result.unwrap()
    if isinstance(parameter, ConfiguredParameterDefault):
        return Success(
            (
                ParameterDefault(
                    name=parameter.parameter.name, value=parameter.parameter.default
                ),
                (),
            )
        )
    elif isinstance(parameter, ResolvedParameterDefault):
        return Success(
            (
                ParameterDefault(
                    name=parameter.parameter.name, value=parameter.default
                ),
                parameter.referenced_types,
            )
        )
    else:
        parameter_context = DefaultTypeParameterContext(
            model_symbol_id=inventory.target_identity.symbol_id,
            parameter=parameter,
            workspace_context=workspace_context,
            project_context=project_context,
            workspace_root_project_context=workspace_root_project_context,
            config_manager=config_manager,
        )
        resolve_result = resolve_primitive_parameter_type(parameter=parameter)
        if resolve_result is not None:
            parameter_context = DefaultPrimitiveLiteralTypeParameterContext(
                model_symbol_id=inventory.target_identity.symbol_id,
                parameter=parameter,
                workspace_context=workspace_context,
                project_context=project_context,
                workspace_root_project_context=workspace_root_project_context,
                config_manager=config_manager,
                resolved_type=resolve_result[1],
            )
            if is_supported_primitive_parameter_type(
                parameter_type_name=resolve_result[0]
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
                resolved.referenced_types,
            )
        )


def _create_helper_inventory(
    create: tuple[HelperInventoryItem, ...],
    workspace_context: WorkspaceContext,
    workspace_root_project_context: ProjectContext,
    project_context: ProjectContext,
    config_manager: ConfigManager,
    interaction: InteractionExecutor[str, Path],
) -> Result[None, GyomuError]:
    for create_item in create:
        cache_result = workspace_context.find_file_analysis_context(
            target_identity=create_item.target_identity
        )
        if isinstance(cache_result, Failure):
            return cache_result.alt(
                lambda error: wrap_gyomu_error(
                    error=error, message="fail to get file analysis"
                )
            )
        file_analysis_context = cache_result.unwrap()
        if file_analysis_context is None:
            return Failure(
                GyomuError(
                    "file analysis is not found",
                    operation="create helper inventory",
                    domain="test",
                    reason="unexpected",
                )
            )
        create_parameters: list[ParameterDefault] = []
        referenced_types: list[ReferencedType] = []
        for parameter_info in create_item.parameters:
            parameter_result = _define_helper_inventory_parameter(
                inventory=create_item,
                module_analysis=file_analysis_context[0].analysis,
                parameter_info=parameter_info,
                workspace_context=workspace_context,
                workspace_root_project_context=workspace_root_project_context,
                project_context=project_context,
                config_manager=config_manager,
                interaction=interaction,
            )
            if isinstance(parameter_result, Failure):
                return parameter_result
            tuple_value = parameter_result.unwrap()
            create_parameters.append(tuple_value[0])
            print(tuple_value[1])
            referenced_types.extend(tuple_value[1])
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
        unique_ref_types = deduplicate_referenced_types(
            referenced_types=referenced_types
        )

        # decide which helpers file to be updated/created
        helper_file_result = get_helper_file_path(
            model_identity=create_item.target_identity, project_context=project_context
        )
        if isinstance(helper_file_result, Failure):
            return helper_file_result.alt(
                lambda error: wrap_gyomu_error(
                    error=error, message="fail to retrieve helper file"
                )
            )
        helper_file_path = ProjectRelativePath(
            helper_file_result.unwrap().relative_to(
                workspace_root_project_context.project_root
            )
        )
        file_result = load_file_analysis_context(
            workspace_root_project_context, helper_file_path
        )
        if isinstance(file_result, Failure):
            return file_result.alt(
                lambda error: wrap_gyomu_error(
                    error=error, message="fail to load helper file"
                )
            )
        helper_file_analysis = file_result.unwrap()

        # insert helper function
        update_file_lines: list[str] = []
        update_file_lines.extend(helper_file_analysis.source_lines)
        reflected_item = reflect_updated_inventory(
            inventory=create_item, model_default=model_default
        )
        function_lines = generate_function_code_lines(reflected_item)

        update_file_lines.append("")
        update_file_lines.extend(function_lines)

        # insert import statement
        last_line = get_last_import_line(helper_file_analysis)
        import_lines = generate_import_code_lines(create_item, unique_ref_types)
        update_file_lines[last_line : last_line + 1] = import_lines

        # save helper file
        print(helper_file_path)
        # breakpoint()
        write_result = write_text(
            workspace_root_project_context.project_root / helper_file_path,
            "".join(update_file_lines),
        )
        if isinstance(write_result, Failure):
            return write_result.alt(
                lambda error: wrap_gyomu_error(
                    error=error, message="fail to write file"
                )
            )
        # run ruff format
        # run mypy validation

    return Success(None)


def get_last_import_line(helper_file_analysis: FileAnalysisContext) -> int:
    min_start_line: int = 9999
    for symbol in helper_file_analysis.analysis.symbols:
        start_line = symbol.location.start_line
        if min_start_line > start_line:
            min_start_line = start_line

    max_import_line: int = 0
    for import_symbol in helper_file_analysis.analysis.imports:
        if (
            import_symbol.end_line < min_start_line
            and import_symbol.end_line > max_import_line
        ):
            max_import_line = import_symbol.end_line
    # breakpoint()
    return max_import_line
