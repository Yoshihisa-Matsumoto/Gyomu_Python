from dataclasses import dataclass

from gyomu_config.manager import ConfigManager
from gyomu_python_analysis.path.conversion import source_relative_path_to_python_path
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_python_analysis.resolve.models import (
    LiteralValueType,
    PackageType,
    PrimitiveType,
    ReferencedType,
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
    GenericsStructureAnalysis,
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
from gyomu_test.helper.defaults.referenced_types import deduplicate_referenced_types
from gyomu_test.helper.defaults.resolution import (
    PrimitiveDefaultConfigContext,
    SymbolDefaultConfigContext,
)
from gyomu_test.helper.inventory.config import get_helper_file_path
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
class ResolvedParameter:
    parameter: Parameter
    referenced_types: list[ReferencedType]


@dataclass(frozen=True)
class ResolvedParameterDefault:
    parameter: ParameterInfo
    default: Parameter
    referenced_types: tuple[ReferencedType, ...]


@dataclass(frozen=True)
class ConfiguredParameterDefault:
    parameter: ParameterInfo


@dataclass(frozen=True)
class MissingParameterDefault:
    parameter: ParameterInfo
    missing_types: tuple[ResolvedType, ...]
    # resolved_types: tuple[ResolvedSymbolDefault | ResolvedPrimitiveDefault, ...]


def resolve_primitive_parameter_type(
    parameter: MissingParameterDefault,
) -> tuple[str, PrimitiveType | LiteralValueType] | None:
    if len(parameter.missing_types) != 1:
        return None

    parameter_type = parameter.parameter.parameter_type

    missing_type = parameter.missing_types[0]

    if not isinstance(missing_type, PrimitiveType | LiteralValueType):
        return None

    if parameter_type.structure is not None:
        structure = parameter_type.structure
        if not isinstance(structure, LiteralStructureAnalysis | NameStructureAnalysis):
            return None

    if isinstance(missing_type, PrimitiveType):
        return missing_type.primitive_type, missing_type

    else:
        value = missing_type.value
        if value is None:
            return None
        return type(value).__name__, missing_type


SUPPORTED_DIRECT_PARAMETER_TYPES = frozenset(
    {
        "str",
        "int",
        "bool",
        "float",
    }
)


def is_supported_primitive_parameter_type(parameter_type_name: str) -> bool:
    return parameter_type_name in SUPPORTED_DIRECT_PARAMETER_TYPES


class ParameterConfigurationContext:
    parameter: ParameterInfo
    module_analysis: ModuleAnalysis
    workspace_context: WorkspaceContext
    project_context: ProjectContext
    config_manager: ConfigManager
    class_name: str

    def __init__(
        self,
        parameter: ParameterInfo,
        module_analysis: ModuleAnalysis,
        workspace_context: WorkspaceContext,
        project_context: ProjectContext,
        config_manager: ConfigManager,
        class_name: str,
    ) -> None:
        self.parameter = parameter
        self.module_analysis = module_analysis
        self.workspace_context = workspace_context
        self.project_context = project_context
        self.config_manager = config_manager
        self.class_name = class_name


def _find_helper_function_declaration_identity(
    workspace_context: WorkspaceContext,
    resolved_symbol: SymbolType,
) -> Result[DeclarationIdentity, GyomuTestError]:
    workspace_project_result = find_workspace_project(
        file_context=resolved_symbol.context,
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

    project_context = workspace_context.get_project_context(
        workspace_project.config.name
    )
    if project_context is None:
        return Failure(
            GyomuTestError(
                message=f"package not found: {workspace_project.config.name}"
            )
        )
    helper_file_result = get_helper_file_path(
        model_identity=resolved_symbol.symbol.identity, project_context=project_context
    )
    if isinstance(helper_file_result, Failure):
        return helper_file_result

    file_path = helper_file_result.unwrap().relative_to(
        workspace_context.workspace_root.path
    )

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
    workspace_context: WorkspaceContext,
    project_context: ProjectContext,
    config_manager: ConfigManager,
    referenced_types: list[ReferencedType],
) -> Result[Parameter | None, GyomuTestError]:
    if isinstance(resolved_type, PrimitiveType | LiteralValueType):
        context = PrimitiveDefaultConfigContext(
            type_default=resolved_type,
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
            return Success(default.parameter)

        return Success(None)
    elif isinstance(resolved_type, PackageType):
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
                workspace_context=workspace_context,
                resolved_symbol=resolved_type,
            )
            if isinstance(helper_identity_result, Failure):
                return helper_identity_result
            helper_identity = helper_identity_result.unwrap()
            # print(format_object(helper_identity))
            referenced_types.append(PackageType(symbol_id=helper_identity.symbol_id))
            return Success(CallParameter(callable_identity=helper_identity))
        else:
            symbol_context = SymbolDefaultConfigContext(
                type_default=resolved_type,
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
                return Success(symbol_default.parameter)
            return Success(None)


def _resolve_parameter_default(
    context: ParameterConfigurationContext,
) -> Result[
    tuple[ResolvedParameter | MissingParameterDefault, tuple[ReferencedType, ...]],
    GyomuTestError,
]:
    referenced_types: list[ReferencedType] = []
    # print(f"{context.parameter.name}:{context.parameter.parameter_type.text}")
    if context.parameter.parameter_type.structure is not None:

        def to_result(
            parameter: ResolvedParameter | MissingParameterDefault,
        ) -> tuple[
            ResolvedParameter | MissingParameterDefault,
            tuple[ReferencedType, ...],
        ]:
            return parameter, tuple(referenced_types)

        # print(
        #     f"{context.parameter.name}: {format_object(context.parameter.parameter_type.structure)}"
        # )
        return _resolve_type_expression(
            expression=context.parameter.parameter_type.structure,
            context=context,
            referenced_types=referenced_types,
        ).map(to_result)
    else:
        resolve_type_result = resolve_type_analysis(
            type_analysis=context.parameter.parameter_type,
            parameter_name=context.parameter.name,
            module=context.module_analysis,
            workspace_context=context.workspace_context,
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
            workspace_context=context.workspace_context,
            project_context=context.project_context,
        )
        load_result = load_primitive_parameter_default_config(
            context=primitive_context, config_manager=context.config_manager
        )
        if isinstance(load_result, Failure):
            return load_result
        default = load_result.unwrap()
        if default is not None:
            return Success(
                (
                    ResolvedParameter(
                        parameter=default.parameter,
                        referenced_types=referenced_types,
                    ),
                    tuple(referenced_types),
                )
            )

        return Success(
            (
                MissingParameterDefault(
                    parameter=context.parameter,
                    missing_types=(resolved_type,),
                    # resolved_types=(),
                ),
                tuple(referenced_types),
            )
        )


def _resolve_name_structure(
    expression: NameStructureAnalysis,
    context: ParameterConfigurationContext,
    referenced_types: list[ReferencedType],
) -> Result[
    ResolvedParameter | MissingParameterDefault,
    GyomuTestError,
]:
    name_structure_result = resolve_name_structure(
        structure=expression,
        parameter_name=context.parameter.name,
        module=context.module_analysis,
        workspace_context=context.workspace_context,
        class_name=context.class_name,
    )
    if isinstance(name_structure_result, Failure):
        return name_structure_result.alt(
            lambda error: GyomuTestError("fail to resolve name structure").chain(error)
        )
    name_structure = name_structure_result.unwrap()
    name_parameter_result = _create_parameter(
        resolved_type=name_structure,
        workspace_context=context.workspace_context,
        project_context=context.project_context,
        config_manager=context.config_manager,
        referenced_types=referenced_types,
    )
    if isinstance(name_parameter_result, Failure):
        return name_parameter_result
    name_parameter = name_parameter_result.unwrap()
    # print(format_object(name_structure, depth=8))
    if isinstance(name_structure, SymbolType | PackageType):
        referenced_types.append(name_structure)
    if name_parameter is not None:
        return Success(
            ResolvedParameter(
                parameter=name_parameter, referenced_types=referenced_types
            )
        )
    return Success(
        MissingParameterDefault(
            parameter=context.parameter,
            missing_types=(name_structure,),
            # resolved_types=(),
        )
    )


def _resolve_union_structure(
    expression: UnionStructureAnalysis,
    context: ParameterConfigurationContext,
    referenced_types: list[ReferencedType],
) -> Result[
    ResolvedParameter | MissingParameterDefault,
    GyomuTestError,
]:
    missing_types: list[ResolvedType] = []
    # union_resolved_types: list[ResolvedSymbolDefault | ResolvedPrimitiveDefault] = []

    for member in expression.types:
        member_result = _resolve_type_expression(
            expression=member, context=context, referenced_types=referenced_types
        )

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
    expression: AttributeStructureAnalysis,
    context: ParameterConfigurationContext,
    referenced_types: list[ReferencedType],
) -> Result[
    ResolvedParameter | MissingParameterDefault,
    GyomuTestError,
]:
    parameter_value: ResolvedParameter | MissingParameterDefault | None = None
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
                expression=child, context=context, referenced_types=referenced_types
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
        ResolvedParameter(
            parameter=AttributeParameter(
                value=parameter_value.parameter, attribute=".".join(attributes)
            ),
            referenced_types=parameter_value.referenced_types,
        )
    )


def _resolve_literal_structure(
    expression: LiteralStructureAnalysis,
    context: ParameterConfigurationContext,
    referenced_types: list[ReferencedType],
) -> Result[
    ResolvedParameter | MissingParameterDefault,
    GyomuTestError,
]:
    return _resolve_type_expression(
        expression.value, context, referenced_types=referenced_types
    )


def _resolve_tuple_structure(
    expression: TupleStructureAnalysis,
    context: ParameterConfigurationContext,
    referenced_types: list[ReferencedType],
) -> Result[
    ResolvedParameter | MissingParameterDefault,
    GyomuTestError,
]:
    # is_elipsis_included: bool = False
    missing_types: list[ResolvedType] = []
    # resolved_types: list[ResolvedSymbolDefault | ResolvedPrimitiveDefault] = []
    tuple_element_parameters: list[Parameter] = []
    for element in expression.elements:
        if isinstance(element, EllipsisStructureAnalysis):
            # is_elipsis_included = True
            break
        else:
            element_result = _resolve_type_expression(
                expression=element, context=context, referenced_types=referenced_types
            )
            if isinstance(element_result, Failure):
                return element_result
            element_parameter = element_result.unwrap()
            if isinstance(element_parameter, MissingParameterDefault):
                missing_types.extend(element_parameter.missing_types)
                # resolved_types.extend(element_parameter.resolved_types)
            else:
                tuple_element_parameters.append(element_parameter.parameter)

    if len(missing_types) == 0:
        return Success(
            ResolvedParameter(
                parameter=TupleParameter(elements=tuple(tuple_element_parameters)),
                referenced_types=referenced_types,
            )
        )
    else:
        return Success(
            MissingParameterDefault(
                parameter=context.parameter,
                missing_types=tuple(missing_types),
                # resolved_types=tuple(resolved_types),
            )
        )


def _resolve_array_structure(
    expression: ArrayStructureAnalysis,
    context: ParameterConfigurationContext,
    referenced_types: list[ReferencedType],
) -> Result[
    ResolvedParameter | MissingParameterDefault,
    GyomuTestError,
]:
    element_result = _resolve_type_expression(
        expression=expression.element,
        context=context,
        referenced_types=referenced_types,
    )
    if isinstance(element_result, Failure):
        return element_result
    element = element_result.unwrap()
    if isinstance(element, MissingParameterDefault):
        return Success(element)

    return Success(
        ResolvedParameter(
            ListParameter(elements=(element.parameter,)),
            referenced_types=referenced_types,
        )
    )


def _resolve_dictionary_structure(
    expression: DictionaryStructureAnalysis,
    context: ParameterConfigurationContext,
    referenced_types: list[ReferencedType],
) -> Result[
    ResolvedParameter | MissingParameterDefault,
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
    key_result = _resolve_type_expression(
        expression=expression.keys, context=context, referenced_types=referenced_types
    )

    if isinstance(key_result, Failure):
        return key_result
    key = key_result.unwrap()
    if isinstance(key, MissingParameterDefault):
        missing_types.extend(key.missing_types)
        # resolved_types.extend(key.resolved_types)

    value_result = _resolve_type_expression(
        expression=expression.values, context=context, referenced_types=referenced_types
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
        return Success(
            ResolvedParameter(
                DictParameter(
                    entries=(DictEntry(key=key.parameter, value=value.parameter),)
                ),
                referenced_types=referenced_types,
            )
        )
    else:
        return Success(
            MissingParameterDefault(
                parameter=context.parameter,
                missing_types=tuple(missing_types),
                # resolved_types=tuple(resolved_types),
            )
        )


def _resolve_generics_structure(
    expression: GenericsStructureAnalysis,
    context: ParameterConfigurationContext,
    referenced_types: list[ReferencedType],
) -> Result[
    ResolvedParameter | MissingParameterDefault,
    GyomuTestError,
]:
    missing_types: list[ResolvedType] = []
    generics_element_parameters: list[Parameter] = []
    key_result = _resolve_type_expression(
        expression=expression.base, context=context, referenced_types=referenced_types
    )

    if isinstance(key_result, Failure):
        return key_result
    key = key_result.unwrap()
    if isinstance(key, MissingParameterDefault):
        missing_types.extend(key.missing_types)
    else:
        generics_element_parameters.append(key.parameter)

    for parameter in expression.parameters:
        element_result = _resolve_type_expression(
            expression=parameter, context=context, referenced_types=referenced_types
        )
        if isinstance(element_result, Failure):
            return element_result
        element_parameter = element_result.unwrap()
        if isinstance(element_parameter, MissingParameterDefault):
            missing_types.extend(element_parameter.missing_types)
            # resolved_types.extend(element_parameter.resolved_types)
        else:
            generics_element_parameters.append(element_parameter.parameter)
    # print(format_object(referenced_types, depth=8))
    # print("----")
    if len(missing_types) == 0:
        return Success(
            ResolvedParameter(
                parameter=TupleParameter(elements=tuple(generics_element_parameters)),
                referenced_types=referenced_types,
            )
        )
    else:
        return Success(
            MissingParameterDefault(
                parameter=context.parameter,
                missing_types=tuple(missing_types),
                # resolved_types=tuple(resolved_types),
            )
        )


def _resolve_type_expression(
    expression: TypeExpression,
    context: ParameterConfigurationContext,
    referenced_types: list[ReferencedType],
) -> Result[
    ResolvedParameter | MissingParameterDefault,
    GyomuTestError,
]:
    if isinstance(expression, LiteralValue):
        referenced_types.append(PackageType(symbol_id=SymbolId("typing::Literal")))
        return Success(
            ResolvedParameter(
                parameter=LiteralParameter(value=expression.value),
                referenced_types=referenced_types,
            )
        )

    elif isinstance(expression, NoneStructureAnalysis):
        return Success(
            ResolvedParameter(
                parameter=NoneParameter(), referenced_types=referenced_types
            )
        )
    elif isinstance(expression, NameStructureAnalysis):
        return _resolve_name_structure(
            expression=expression, context=context, referenced_types=referenced_types
        )

    elif isinstance(expression, UnionStructureAnalysis):
        return _resolve_union_structure(
            expression=expression, context=context, referenced_types=referenced_types
        )
    elif isinstance(expression, AttributeStructureAnalysis):
        return _resolve_attribute_structure(
            expression=expression, context=context, referenced_types=referenced_types
        )
    elif isinstance(expression, TupleStructureAnalysis):
        return _resolve_tuple_structure(
            expression=expression, context=context, referenced_types=referenced_types
        )
    elif isinstance(expression, LiteralStructureAnalysis):
        return _resolve_literal_structure(
            expression=expression, context=context, referenced_types=referenced_types
        )
    elif isinstance(expression, ArrayStructureAnalysis):
        return _resolve_array_structure(
            expression=expression, context=context, referenced_types=referenced_types
        )
    elif isinstance(expression, DictionaryStructureAnalysis):
        return _resolve_dictionary_structure(
            expression=expression, context=context, referenced_types=referenced_types
        )
    elif isinstance(expression, GenericsStructureAnalysis):
        return _resolve_generics_structure(
            expression=expression, context=context, referenced_types=referenced_types
        )
    return Failure(
        GyomuTestError(
            "Unsupported ", details={"type-of-expression": type(expression).__name__}
        )
    )


def resolve_function_parameter_default(
    inventory: HelperInventoryItem,
    parameter_info: ParameterInfo,
    module_analysis: ModuleAnalysis,
    workspace_context: WorkspaceContext,
    project_context: ProjectContext,
    config_manager: ConfigManager,
) -> Result[
    tuple[
        ConfiguredParameterDefault | ResolvedParameterDefault | MissingParameterDefault,
        tuple[ReferencedType, ...],
    ],
    GyomuTestError,
]:

    context = ParameterConfigurationContext(
        parameter=parameter_info,
        module_analysis=module_analysis,
        workspace_context=workspace_context,
        project_context=project_context,
        config_manager=config_manager,
        class_name=inventory.target_identity.get_symbol_name(),
    )
    # print(format_object(parameter_info))
    default_result = _resolve_parameter_default(context=context)
    if isinstance(default_result, Failure):
        return default_result
    resolved_default, referenced_types = default_result.unwrap()

    # print(f"referenced_types: {len(referenced_types)}")
    if parameter_info.default is not None:
        return Success((ConfiguredParameterDefault(parameter_info), referenced_types))
    if isinstance(resolved_default, MissingParameterDefault):
        return Success((resolved_default, referenced_types))

    return Success(
        (
            ResolvedParameterDefault(
                parameter=parameter_info,
                default=resolved_default.parameter,
                referenced_types=deduplicate_referenced_types(
                    resolved_default.referenced_types
                ),
            ),
            referenced_types,
        )
    )


def _resolve_function_parameter_defaults(
    inventory: HelperInventoryItem,
    workspace_context: WorkspaceContext,
    project_context: ProjectContext,
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
    cache_result = workspace_context.find_file_analysis_context(
        target_identity=inventory.target_identity
    )
    if isinstance(cache_result, Failure):
        return cache_result.alt(
            lambda error: GyomuTestError(message="fail to get file analysis").chain(
                error
            )
        )
    file_analysis_context = cache_result.unwrap()
    if file_analysis_context is None:
        return Failure(GyomuTestError("test"))

    for parameter in inventory.parameters:
        parameter_result = resolve_function_parameter_default(
            inventory=inventory,
            parameter_info=parameter,
            module_analysis=file_analysis_context[0].analysis,
            workspace_context=workspace_context,
            project_context=project_context,
            config_manager=config_manager,
        )
        if isinstance(parameter_result, Failure):
            return parameter_result
        else:
            result.append(parameter_result.unwrap()[0])

    return Success(tuple(result))
