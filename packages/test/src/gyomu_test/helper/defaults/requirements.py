from dataclasses import dataclass

from gyomu_config.manager import ConfigManager
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import WorkspaceContext, WorkspaceRoot
from gyomu_python_analysis.resolve.file_analysis_cache import FileAnalysisCache
from gyomu_python_analysis.resolve.models import (
    AttributeType,
    LiteralValueType,
    PrimitiveType,
    ResolvedType,
    SymbolType,
)
from gyomu_python_analysis.resolve.type_reference import (
    resolve_name_structure,
    resolve_type_analysis,
)
from gyomu_schema.schemas.config.test.model_defaults import (
    AttributeParameter,
    LiteralParameter,
    ModelDefault,
    NoneParameter,
    Parameter,
    PrimitiveDefault,
)
from gyomu_schema.schemas.python.module import ModuleAnalysis
from gyomu_schema.schemas.python.type.structure import (
    LiteralValue,
    NameStructureAnalysis,
    NoneStructureAnalysis,
)
from gyomu_schema.schemas.python.type.type_analysis import (
    AttributeStructureAnalysis,
    TypeExpression,
    UnionStructureAnalysis,
)
from gyomu_schema.schemas.testing.helper import (
    HelperInventoryItem,
    ParameterInfo,
    TargetClassKind,
)
from returns.result import Failure, Result, Success

from gyomu_test.error.test import GyomuTestError
from gyomu_test.helper.defaults.load import (
    load_primitive_parameter_default_config,
    load_symbol_parameter_default_config,
)
from gyomu_test.helper.defaults.resolution import (
    PrimitiveDefaultConfigContext,
    SymbolDefaultConfigContext,
)


@dataclass(frozen=True)
class ResolvedHelperSymbolDefault:
    resolved_type: SymbolType
    model_kind: TargetClassKind


@dataclass(frozen=True)
class ResolvedNonHelperDefault:
    resolved_type: SymbolType
    config: ModelDefault


type ResolvedSymbolDefault = ResolvedHelperSymbolDefault | ResolvedNonHelperDefault


@dataclass(frozen=True)
class ResolvedPrimitiveDefault:
    resolved_type: PrimitiveType | LiteralValueType
    config: PrimitiveDefault


@dataclass(frozen=True)
class MissingParameterDefault:
    parameter: ParameterInfo
    missing_types: tuple[ResolvedType, ...]
    resolved_types: tuple[ResolvedSymbolDefault | ResolvedPrimitiveDefault, ...]


@dataclass(frozen=True)
class ResolvedParameterDefault:
    parameter: ParameterInfo
    default: Parameter


@dataclass(frozen=True)
class ConfiguredParameterDefault:
    parameter: ParameterInfo


def _create_parameter(
    resolved_type: ResolvedType,
    workspace_root: WorkspaceRoot,
    workspace_context: WorkspaceContext,
    project_context: ProjectContext,
    config_manager: ConfigManager,
) -> Result[Parameter | None, GyomuTestError]:
    if isinstance(resolved_type, PrimitiveType | LiteralValueType):
        context = PrimitiveDefaultConfigContext(
            type_default=resolved_type,
            workspace_root=workspace_root,
            workspace_context=workspace_context,
            project_context=project_context,
        )
        load_result = load_primitive_parameter_default_config(
            context=context, config_manager=config_manager
        )
        if isinstance(load_result, Failure):
            return load_result
        default = load_result.unwrap()
        if default is not None:
            if default.parameters[0].value is not None:
                return Success(default.parameters[0].value)

        return Success(None)
    else:
        symbol_context = SymbolDefaultConfigContext(
            type_default=resolved_type,
            workspace_root=workspace_root,
            workspace_context=workspace_context,
            project_context=project_context,
        )
        symbol_load_result = load_symbol_parameter_default_config(
            context=symbol_context, config_manager=config_manager
        )
        if isinstance(symbol_load_result, Failure):
            return symbol_load_result
        symbol_default = symbol_load_result.unwrap()
        if symbol_default is not None:
            if symbol_default.parameters[0].value is not None:
                return Success(symbol_default.parameters[0].value)
        return Success(None)


def _resolve_parameter_default(
    parameter: ParameterInfo,
    module: ModuleAnalysis,
    workspace_root: WorkspaceRoot,
    workspace_context: WorkspaceContext,
    project_context: ProjectContext,
    file_analysis_cache: FileAnalysisCache,
    config_manager: ConfigManager,
    class_name: str,
) -> Result[Parameter | MissingParameterDefault, GyomuTestError]:
    if parameter.parameter_type.structure is not None:
        return _resolve_type_expression(
            expression=parameter.parameter_type.structure,
            parameter=parameter,
            module=module,
            workspace_root=workspace_root,
            workspace_context=workspace_context,
            project_context=project_context,
            file_analysis_cache=file_analysis_cache,
            config_manager=config_manager,
            class_name=class_name,
        )
    else:
        # parameter.parameter_type.text　にPrimitive型があるから、それから設定を読んであればParameter作る、なければMissingParameterDefault
        resolve_type_result = resolve_type_analysis(
            type_analysis=parameter.parameter_type,
            parameter_name=parameter.name,
            module=module,
            project_context=project_context,
            file_analysis_cache=file_analysis_cache,
        )
        if isinstance(resolve_type_result, Failure):
            return resolve_type_result.alt(
                lambda error: GyomuTestError(
                    "fail to resolve type from type text"
                ).chain(error)
            )
        resolved_type = resolve_type_result.unwrap()[0]
        if not isinstance(resolved_type, PrimitiveType):
            return Failure(GyomuTestError("should be primitive type"))
        context = PrimitiveDefaultConfigContext(
            type_default=resolved_type,
            workspace_root=workspace_root,
            workspace_context=workspace_context,
            project_context=project_context,
        )
        load_result = load_primitive_parameter_default_config(
            context=context, config_manager=config_manager
        )
        if isinstance(load_result, Failure):
            return load_result
        default = load_result.unwrap()
        if default is not None:
            if default.parameters[0].value is not None:
                return Success(default.parameters[0].value)

        return Success(
            MissingParameterDefault(
                parameter=parameter, missing_types=(resolved_type,), resolved_types=()
            )
        )


def _resolve_name_structure(
    expression: NameStructureAnalysis,
    parameter: ParameterInfo,
    module: ModuleAnalysis,
    workspace_root: WorkspaceRoot,
    workspace_context: WorkspaceContext,
    project_context: ProjectContext,
    file_analysis_cache: FileAnalysisCache,
    config_manager: ConfigManager,
    class_name: str,
) -> Result[
    Parameter | MissingParameterDefault,
    GyomuTestError,
]:
    name_structure_result = resolve_name_structure(
        structure=expression,
        parameter_name=parameter.name,
        module=module,
        project_context=project_context,
        file_analysis_cache=file_analysis_cache,
        class_name=class_name,
        need_resolve_name=True,
    )
    if isinstance(name_structure_result, Failure):
        return name_structure_result.alt(
            lambda error: GyomuTestError("fail to resolve name structure").chain(error)
        )
    name_structure = name_structure_result.unwrap()
    assert not isinstance(name_structure, AttributeType)
    name_parameter_result = _create_parameter(
        resolved_type=name_structure,
        workspace_root=workspace_root,
        workspace_context=workspace_context,
        project_context=project_context,
        config_manager=config_manager,
    )
    if isinstance(name_parameter_result, Failure):
        return name_parameter_result
    name_parameter = name_parameter_result.unwrap()
    if name_parameter is not None:
        return Success(name_parameter)
    return Success(
        MissingParameterDefault(
            parameter=parameter, missing_types=(name_structure,), resolved_types=()
        )
    )


def _resolve_union_structure(
    expression: UnionStructureAnalysis,
    parameter: ParameterInfo,
    module: ModuleAnalysis,
    workspace_root: WorkspaceRoot,
    workspace_context: WorkspaceContext,
    project_context: ProjectContext,
    file_analysis_cache: FileAnalysisCache,
    config_manager: ConfigManager,
    class_name: str,
) -> Result[
    Parameter | MissingParameterDefault,
    GyomuTestError,
]:
    missing_types: list[ResolvedType] = []
    union_resolved_types: list[ResolvedSymbolDefault | ResolvedPrimitiveDefault] = []

    for member in expression.types:
        member_result = _resolve_type_expression(
            expression=member,
            parameter=parameter,
            module=module,
            workspace_root=workspace_root,
            workspace_context=workspace_context,
            project_context=project_context,
            file_analysis_cache=file_analysis_cache,
            config_manager=config_manager,
            class_name=class_name,
        )

        if isinstance(member_result, Failure):
            return member_result

        member_default = member_result.unwrap()

        if not isinstance(member_default, MissingParameterDefault):
            return Success(member_default)

        missing_types.extend(member_default.missing_types)
        union_resolved_types.extend(member_default.resolved_types)

    return Success(
        MissingParameterDefault(
            parameter=parameter,
            missing_types=tuple(missing_types),
            resolved_types=tuple(union_resolved_types),
        )
    )


def _resolve_attribute_structure(
    expression: AttributeStructureAnalysis,
    parameter: ParameterInfo,
    module: ModuleAnalysis,
    workspace_root: WorkspaceRoot,
    workspace_context: WorkspaceContext,
    project_context: ProjectContext,
    file_analysis_cache: FileAnalysisCache,
    config_manager: ConfigManager,
    class_name: str,
) -> Result[
    Parameter | MissingParameterDefault,
    GyomuTestError,
]:
    parameter_value: Parameter | MissingParameterDefault | None = None
    attributes: list[str] = []
    for index, child in enumerate(expression.values):
        if not isinstance(child, NameStructureAnalysis):
            return Failure(
                GyomuTestError(
                    "child in AttributeStructure must be Name Structure",
                    details={"child": child},
                )
            )
        if index == 0:
            parameter_value_result = _resolve_name_structure(
                expression=child,
                parameter=parameter,
                module=module,
                workspace_root=workspace_root,
                workspace_context=workspace_context,
                project_context=project_context,
                file_analysis_cache=file_analysis_cache,
                config_manager=config_manager,
                class_name=class_name,
            )
            if isinstance(parameter_value_result, Failure):
                return parameter_value_result
            parameter_value = parameter_value_result.unwrap()
        else:
            attributes.append(child.name)

    if parameter_value is None:
        return Failure(
            GyomuTestError(
                "AttributeStructure must have at least one element + ene child"
            )
        )
    if isinstance(parameter_value, MissingParameterDefault):
        return Success(parameter_value)

    return Success(
        AttributeParameter(value=parameter_value, attribute=".".join(attributes))
    )


def _resolve_type_expression(
    expression: TypeExpression,
    parameter: ParameterInfo,
    module: ModuleAnalysis,
    workspace_root: WorkspaceRoot,
    workspace_context: WorkspaceContext,
    project_context: ProjectContext,
    file_analysis_cache: FileAnalysisCache,
    config_manager: ConfigManager,
    class_name: str,
) -> Result[
    Parameter | MissingParameterDefault,
    GyomuTestError,
]:
    if isinstance(expression, LiteralValue):
        return Success(LiteralParameter(value=parameter.name))

    elif isinstance(expression, NoneStructureAnalysis):
        return Success(NoneParameter())
    elif isinstance(expression, NameStructureAnalysis):
        return _resolve_name_structure(
            expression=expression,
            parameter=parameter,
            module=module,
            workspace_root=workspace_root,
            workspace_context=workspace_context,
            project_context=project_context,
            file_analysis_cache=file_analysis_cache,
            config_manager=config_manager,
            class_name=class_name,
        )

    elif isinstance(expression, UnionStructureAnalysis):
        return _resolve_union_structure(
            expression=expression,
            parameter=parameter,
            module=module,
            workspace_root=workspace_root,
            workspace_context=workspace_context,
            project_context=project_context,
            file_analysis_cache=file_analysis_cache,
            config_manager=config_manager,
            class_name=class_name,
        )
    elif isinstance(expression, AttributeStructureAnalysis):
        return _resolve_attribute_structure(
            expression=expression,
            parameter=parameter,
            module=module,
            workspace_root=workspace_root,
            workspace_context=workspace_context,
            project_context=project_context,
            file_analysis_cache=file_analysis_cache,
            config_manager=config_manager,
            class_name=class_name,
        )

    return Failure(GyomuTestError("Unsupported "))


def _find_parameter_default(
    config: ModelDefault | PrimitiveDefault,
    parameter_name: str,
) -> Parameter | None:
    for item in config.parameters:
        if item.name == parameter_name:
            return item.value

    return None


def resolve_function_parameter_defaults(
    inventory: HelperInventoryItem,
    workspace_root: WorkspaceRoot,
    workspace_context: WorkspaceContext,
    project_context: ProjectContext,
    file_analysis_cache: FileAnalysisCache,
    config_manager: ConfigManager,
) -> Result[
    tuple[
        ConfiguredParameterDefault | ResolvedParameterDefault | MissingParameterDefault,
        ...,
    ],
    GyomuTestError,
]:
    result: list[
        ConfiguredParameterDefault | ResolvedParameterDefault | MissingParameterDefault
    ] = []
    cache_result = file_analysis_cache.get_file_analysis_context(
        project_context=project_context, identity=inventory.target_identity
    )
    if isinstance(cache_result, Failure):
        return cache_result.alt(
            lambda error: GyomuTestError(message="fail to get file analysis").chain(
                error
            )
        )
    file_analysis_context = cache_result.unwrap()

    for parameter in inventory.parameters:
        if parameter.default is not None:
            result.append(ConfiguredParameterDefault(parameter))
            continue

        default_result = _resolve_parameter_default(
            parameter=parameter,
            module=file_analysis_context.analysis,
            workspace_root=workspace_root,
            workspace_context=workspace_context,
            project_context=project_context,
            file_analysis_cache=file_analysis_cache,
            config_manager=config_manager,
            class_name=inventory.target_identity.get_symbol_name(),
        )
        if isinstance(default_result, Failure):
            return default_result

        resolved_default = default_result.unwrap()

        if isinstance(resolved_default, MissingParameterDefault):
            result.append(resolved_default)
            continue

        result.append(
            ResolvedParameterDefault(
                parameter=parameter,
                default=resolved_default,
            )
        )

    return Success(tuple(result))
