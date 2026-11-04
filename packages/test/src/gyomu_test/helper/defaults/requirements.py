from dataclasses import dataclass

from gyomu_config.manager import ConfigManager
from gyomu_python_analysis.path.conversion import source_relative_path_to_python_path
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import WorkspaceContext, WorkspaceRoot
from gyomu_python_analysis.resolve.file_analysis_cache import FileAnalysisCache
from gyomu_python_analysis.resolve.models import (
    LiteralValueType,
    PrimitiveType,
    ResolvedType,
    SymbolType,
)
from gyomu_python_analysis.resolve.project_membership import find_workspace_project
from gyomu_python_analysis.resolve.type_reference import (
    resolve_name_structure,
    resolve_type_analysis,
)
from gyomu_schema.schemas.config.test.model_defaults import (
    AttributeParameter,
    CallParameter,
    DictEntry,
    DictParameter,
    ListParameter,
    LiteralParameter,
    ModelDefault,
    NoneParameter,
    Parameter,
    PrimitiveDefault,
    TupleParameter,
)
from gyomu_schema.schemas.python.module import ModuleAnalysis
from gyomu_schema.schemas.python.type.structure import (
    EllipsisStructureAnalysis,
    LiteralValue,
    NameStructureAnalysis,
    NoneStructureAnalysis,
)
from gyomu_schema.schemas.python.type.type_analysis import (
    ArrayStructureAnalysis,
    AttributeStructureAnalysis,
    DictionaryStructureAnalysis,
    LiteralStructureAnalysis,
    TupleStructureAnalysis,
    TypeExpression,
    UnionStructureAnalysis,
)
from gyomu_schema.schemas.python.types import (
    DeclarationId,
    DeclarationIdentity,
    SourceRelativePath,
    SymbolId,
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
from gyomu_test.helper.inventory.expected import _get_model_kind
from gyomu_test.helper.inventory.naming import _build_helper_name_from_class_name


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
    # resolved_types: tuple[ResolvedSymbolDefault | ResolvedPrimitiveDefault, ...]


@dataclass(frozen=True)
class ResolvedParameterDefault:
    parameter: ParameterInfo
    default: Parameter


@dataclass(frozen=True)
class ConfiguredParameterDefault:
    parameter: ParameterInfo


class ParameterConfigurationContext:
    parameter: ParameterInfo
    module: ModuleAnalysis
    workspace_root: WorkspaceRoot
    workspace_context: WorkspaceContext
    project_context: ProjectContext
    file_analysis_cache: FileAnalysisCache
    config_manager: ConfigManager
    class_name: str

    def __init__(
        self,
        parameter: ParameterInfo,
        module: ModuleAnalysis,
        workspace_root: WorkspaceRoot,
        workspace_context: WorkspaceContext,
        project_context: ProjectContext,
        file_analysis_cache: FileAnalysisCache,
        config_manager: ConfigManager,
        class_name: str,
    ) -> None:
        self.parameter = parameter
        self.module = module
        self.workspace_root = workspace_root
        self.workspace_context = workspace_context
        self.project_context = project_context
        self.file_analysis_cache = file_analysis_cache
        self.config_manager = config_manager
        self.class_name = class_name


def _find_helper_function_declaration_identity(
    workspace_root: WorkspaceRoot,
    workspace_context: WorkspaceContext,
    resolved_symbol: SymbolType,
) -> Result[DeclarationIdentity, GyomuTestError]:
    workspace_project_result = find_workspace_project(
        file_context=resolved_symbol.context,
        workspace_root=workspace_root,
        workspace_context=workspace_context,
    )
    if isinstance(workspace_project_result, Failure):
        return workspace_project_result.alt(
            lambda e: GyomuTestError(
                "Failed to find workspace project for type default",
                details={"symbol": resolved_symbol.symbol.identity},
            ).chain(e)
        )
    workspace_project = workspace_project_result.unwrap()
    file_path = workspace_project.path / "test_support" / "helpers.py"
    module_path = source_relative_path_to_python_path(
        path=SourceRelativePath(file_path)
    )
    function_name = _build_helper_name_from_class_name(
        class_name=resolved_symbol.symbol.name
    )
    python_path = f"{module_path}::{function_name}"
    return Success(
        DeclarationIdentity(
            symbol_id=SymbolId(python_path), declaration_id=DeclarationId(".")
        )
    )


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
        if default is not None and default.parameters[0].value is not None:
            return Success(default.parameters[0].value)

        return Success(None)
    else:
        model_kind_result = _get_model_kind(
            symbol=resolved_type.symbol,
            module=resolved_type.context.analysis,
            workspace=workspace_context,
        )
        if isinstance(model_kind_result, Failure):
            return model_kind_result.alt(
                lambda error: GyomuTestError("fail to retrieve model kind").chain(error)
            )
        model_kind = model_kind_result.unwrap()
        if model_kind is not None:
            helper_identity_result = _find_helper_function_declaration_identity(
                workspace_root=workspace_root,
                workspace_context=workspace_context,
                resolved_symbol=resolved_type,
            )
            if isinstance(helper_identity_result, Failure):
                return helper_identity_result
            return Success(
                CallParameter(callable_identity=helper_identity_result.unwrap())
            )
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
            if (
                symbol_default is not None
                and symbol_default.parameters[0].value is not None
            ):
                return Success(symbol_default.parameters[0].value)
            return Success(None)


def _resolve_parameter_default(
    context: ParameterConfigurationContext,
) -> Result[Parameter | MissingParameterDefault, GyomuTestError]:
    if context.parameter.parameter_type.structure is not None:
        return _resolve_type_expression(
            expression=context.parameter.parameter_type.structure, context=context
        )
    else:
        # parameter.parameter_type.text　にPrimitive型があるから、それから設定を読んであればParameter作る、なければMissingParameterDefault
        resolve_type_result = resolve_type_analysis(
            type_analysis=context.parameter.parameter_type,
            parameter_name=context.parameter.name,
            module=context.module,
            project_context=context.project_context,
            file_analysis_cache=context.file_analysis_cache,
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
        primitive_context = PrimitiveDefaultConfigContext(
            type_default=resolved_type,
            workspace_root=context.workspace_root,
            workspace_context=context.workspace_context,
            project_context=context.project_context,
        )
        load_result = load_primitive_parameter_default_config(
            context=primitive_context, config_manager=context.config_manager
        )
        if isinstance(load_result, Failure):
            return load_result
        default = load_result.unwrap()
        if default is not None and default.parameters[0].value is not None:
            return Success(default.parameters[0].value)

        return Success(
            MissingParameterDefault(
                parameter=context.parameter,
                missing_types=(resolved_type,),
                # resolved_types=(),
            )
        )


def _resolve_name_structure(
    expression: NameStructureAnalysis, context: ParameterConfigurationContext
) -> Result[
    Parameter | MissingParameterDefault,
    GyomuTestError,
]:
    name_structure_result = resolve_name_structure(
        structure=expression,
        parameter_name=context.parameter.name,
        module=context.module,
        project_context=context.project_context,
        file_analysis_cache=context.file_analysis_cache,
        class_name=context.class_name,
    )
    if isinstance(name_structure_result, Failure):
        return name_structure_result.alt(
            lambda error: GyomuTestError("fail to resolve name structure").chain(error)
        )
    name_structure = name_structure_result.unwrap()
    name_parameter_result = _create_parameter(
        resolved_type=name_structure,
        workspace_root=context.workspace_root,
        workspace_context=context.workspace_context,
        project_context=context.project_context,
        config_manager=context.config_manager,
    )
    if isinstance(name_parameter_result, Failure):
        return name_parameter_result
    name_parameter = name_parameter_result.unwrap()
    if name_parameter is not None:
        return Success(name_parameter)
    return Success(
        MissingParameterDefault(
            parameter=context.parameter,
            missing_types=(name_structure,),
            # resolved_types=(),
        )
    )


def _resolve_union_structure(
    expression: UnionStructureAnalysis, context: ParameterConfigurationContext
) -> Result[
    Parameter | MissingParameterDefault,
    GyomuTestError,
]:
    missing_types: list[ResolvedType] = []
    # union_resolved_types: list[ResolvedSymbolDefault | ResolvedPrimitiveDefault] = []

    for member in expression.types:
        member_result = _resolve_type_expression(expression=member, context=context)

        if isinstance(member_result, Failure):
            return member_result

        member_default = member_result.unwrap()

        if not isinstance(member_default, MissingParameterDefault):
            return Success(member_default)

        missing_types.extend(member_default.missing_types)
        # union_resolved_types.extend(member_default.resolved_types)

    return Success(
        MissingParameterDefault(
            parameter=context.parameter,
            missing_types=tuple(missing_types),
            # resolved_types=tuple(union_resolved_types),
        )
    )


def _resolve_attribute_structure(
    expression: AttributeStructureAnalysis, context: ParameterConfigurationContext
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
                expression=child, context=context
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


def _resolve_literal_structure(
    expression: LiteralStructureAnalysis, context: ParameterConfigurationContext
) -> Result[
    Parameter | MissingParameterDefault,
    GyomuTestError,
]:
    return _resolve_type_expression(expression.value, context)


def _resolve_tuple_structure(
    expression: TupleStructureAnalysis, context: ParameterConfigurationContext
) -> Result[
    Parameter | MissingParameterDefault,
    GyomuTestError,
]:
    is_elipsis_included: bool = False
    missing_types: list[ResolvedType] = []
    # resolved_types: list[ResolvedSymbolDefault | ResolvedPrimitiveDefault] = []
    tuple_element_parameters: list[Parameter] = []
    for element in expression.elements:
        if isinstance(element, EllipsisStructureAnalysis):
            is_elipsis_included = True
            break
        else:
            element_result = _resolve_type_expression(
                expression=element, context=context
            )
            if isinstance(element_result, Failure):
                return element_result
            element_parameter = element_result.unwrap()
            if isinstance(element_parameter, MissingParameterDefault):
                missing_types.extend(element_parameter.missing_types)
                # resolved_types.extend(element_parameter.resolved_types)
            else:
                tuple_element_parameters.append(element_parameter)

    if len(missing_types) == 0:
        return Success(TupleParameter(elements=tuple(tuple_element_parameters)))
    else:
        return Success(
            MissingParameterDefault(
                parameter=context.parameter,
                missing_types=tuple(missing_types),
                # resolved_types=tuple(resolved_types),
            )
        )


def _resolve_array_structure(
    expression: ArrayStructureAnalysis, context: ParameterConfigurationContext
) -> Result[
    Parameter | MissingParameterDefault,
    GyomuTestError,
]:
    element_result = _resolve_type_expression(
        expression=expression.element, context=context
    )
    if isinstance(element_result, Failure):
        return element_result
    element = element_result.unwrap()
    if isinstance(element, MissingParameterDefault):
        return Success(element)

    return Success(ListParameter(elements=(element,)))


def _resolve_dictionary_structure(
    expression: DictionaryStructureAnalysis, context: ParameterConfigurationContext
) -> Result[
    Parameter | MissingParameterDefault,
    GyomuTestError,
]:
    if expression.keys is None or expression.values is None:
        return Success(
            MissingParameterDefault(
                parameter=context.parameter,
                missing_types=(),
            )
        )
    missing_types: list[ResolvedType] = []
    # resolved_types: list[ResolvedSymbolDefault | ResolvedPrimitiveDefault] = []
    key_result = _resolve_type_expression(expression=expression.keys, context=context)

    if isinstance(key_result, Failure):
        return key_result
    key = key_result.unwrap()
    if isinstance(key, MissingParameterDefault):
        missing_types.extend(key.missing_types)
        # resolved_types.extend(key.resolved_types)

    value_result = _resolve_type_expression(
        expression=expression.values, context=context
    )
    if isinstance(value_result, Failure):
        return value_result
    value = value_result.unwrap()
    if isinstance(value, MissingParameterDefault):
        missing_types.extend(value.missing_types)
        # resolved_types.extend(value.resolved_types)

    if not isinstance(key, MissingParameterDefault) and not isinstance(
        value, MissingParameterDefault
    ):
        return Success(DictParameter(entries=(DictEntry(key=key, value=value),)))
    else:
        return Success(
            MissingParameterDefault(
                parameter=context.parameter,
                missing_types=tuple(missing_types),
                # resolved_types=tuple(resolved_types),
            )
        )


def _resolve_type_expression(
    expression: TypeExpression, context: ParameterConfigurationContext
) -> Result[
    Parameter | MissingParameterDefault,
    GyomuTestError,
]:
    if isinstance(expression, LiteralValue):
        return Success(LiteralParameter(value=expression.value))

    elif isinstance(expression, NoneStructureAnalysis):
        return Success(NoneParameter())
    elif isinstance(expression, NameStructureAnalysis):
        return _resolve_name_structure(expression=expression, context=context)

    elif isinstance(expression, UnionStructureAnalysis):
        return _resolve_union_structure(expression=expression, context=context)
    elif isinstance(expression, AttributeStructureAnalysis):
        return _resolve_attribute_structure(expression=expression, context=context)
    elif isinstance(expression, TupleStructureAnalysis):
        return _resolve_tuple_structure(expression=expression, context=context)
    elif isinstance(expression, LiteralStructureAnalysis):
        return _resolve_literal_structure(expression=expression, context=context)
    elif isinstance(expression, ArrayStructureAnalysis):
        return _resolve_array_structure(expression=expression, context=context)
    elif isinstance(expression, DictionaryStructureAnalysis):
        return _resolve_dictionary_structure(expression=expression, context=context)
    return Failure(
        GyomuTestError(
            "Unsupported ", details={"type-of-expression": type(expression).__name__}
        )
    )


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

        context = ParameterConfigurationContext(
            parameter=parameter,
            module=file_analysis_context.analysis,
            workspace_root=workspace_root,
            workspace_context=workspace_context,
            project_context=project_context,
            file_analysis_cache=file_analysis_cache,
            config_manager=config_manager,
            class_name=inventory.target_identity.get_symbol_name(),
        )

        default_result = _resolve_parameter_default(context=context)
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
