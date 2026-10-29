from gyomu_config.file.retrieve import retrieve_config
from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_python_analysis.resolve.cls import (
    collect_class_hierarchy,
    inherits_from_gyomu_base_error,
    inherits_from_pydantic_basemodel,
    is_dataclass_class,
)
from gyomu_python_analysis.resolve.load_file_context import load_file_analysis_context
from gyomu_python_analysis.resolve.models import ClassResolutionCollection
from gyomu_schema.option.analysis import AnalysisOption
from gyomu_schema.schemas.config.test.model_defaults import (
    ModelDefault,
    ModelDefaults,
    Parameter,
)
from gyomu_schema.schemas.python.class_analysis import (
    ClassAnalysis,
    ClassVariableAnalysis,
)
from gyomu_schema.schemas.python.module import ModuleAnalysis
from gyomu_schema.schemas.python.parameter import ParameterAnalysis
from gyomu_schema.schemas.python.symbol import SymbolAnalysis
from gyomu_schema.schemas.python.types import DeclarationIdentity
from gyomu_schema.schemas.testing.helper import (
    HelperInventoryItem,
    ParameterInfo,
    TargetClassKind,
)
from returns.result import Failure, Result, Success

from gyomu_test.error.inventory import (
    FileInventoryError,
    MissingTypeAnnotation,
    ProjectInventoryError,
)
from gyomu_test.error.test import GyomuTestError
from gyomu_test.helper.inventory.config import build_config_request
from gyomu_test.helper.inventory.naming import (
    _build_helper_name_from_class_name,
)


def _get_model_kind(
    symbol: SymbolAnalysis,
    module: ModuleAnalysis,
    workspace: WorkspaceContext,
) -> Result[TargetClassKind | None, AnalysisError]:
    if not isinstance(symbol, ClassAnalysis):
        return Success(None)
    cls = symbol
    if is_dataclass_class(cls, module):
        return Success(TargetClassKind.DATACLASS)
    pydantic_result = inherits_from_pydantic_basemodel(cls, module, workspace)
    if isinstance(pydantic_result, Failure):
        return pydantic_result
    if pydantic_result.unwrap():
        return Success(TargetClassKind.PYDANTIC_MODEL)

    gyomu_error_result = inherits_from_gyomu_base_error(cls, module, workspace)
    if isinstance(gyomu_error_result, Failure):
        return gyomu_error_result
    if gyomu_error_result.unwrap():
        return Success(TargetClassKind.GYOMU_ERROR)
    return Success(None)


def _build_helper_function_parameter(
    variable: ClassVariableAnalysis, default: Parameter | None
) -> Result[ParameterInfo, MissingTypeAnnotation]:
    if variable.type is None:
        return Failure(MissingTypeAnnotation(identity=variable.identity))
    return Success(
        ParameterInfo(name=variable.name, parameter_type=variable.type, default=default)
    )


def _build_helper_function_parameter_analysis(
    parameter_analysis: ParameterAnalysis,
    identity: DeclarationIdentity,
    default: Parameter | None,
) -> Result[ParameterInfo, MissingTypeAnnotation]:
    if parameter_analysis.type is None:
        return Failure(MissingTypeAnnotation(identity=identity))
    return Success(
        ParameterInfo(
            name=parameter_analysis.name,
            parameter_type=parameter_analysis.type,
            default=default,
        )
    )


def _find_parameter(
    variable_name: str, default: ModelDefault | None
) -> Parameter | None:
    if default is None:
        return None
    return next(
        (param.value for param in default.parameters if param.name == variable_name),
        None,
    )


def _build_model_helper_inventory_item(
    symbol: ClassAnalysis,
    collections_sorted_base_first: ClassResolutionCollection,
    model_kind: TargetClassKind,
    default: ModelDefault | None,
) -> Result[
    HelperInventoryItem,
    tuple[MissingTypeAnnotation, ...],
]:

    parameters: list[ParameterInfo] = []
    type_errors: list[MissingTypeAnnotation] = []
    if model_kind != TargetClassKind.GYOMU_ERROR:
        for resolved in collections_sorted_base_first.resolved():
            for param in resolved.symbol.variables:
                if (
                    model_kind == TargetClassKind.PYDANTIC_MODEL
                    and param.name == "model_config"
                ):
                    continue
                target_parameter_default = _find_parameter(
                    variable_name=param.name, default=default
                )
                parameter_result = _build_helper_function_parameter(
                    param, default=target_parameter_default
                )
                if isinstance(parameter_result, Failure):
                    type_errors.append(parameter_result.failure())
                else:
                    parameters.append(parameter_result.unwrap())
    else:
        # for param in symbol.variables:
        #     target_parameter_default = _find_parameter(
        #         variable_name=param.name, default=default
        #     )
        #     parameter_result = _build_helper_function_parameter(
        #         param, default=target_parameter_default
        #     )
        #     if isinstance(parameter_result, Failure):
        #         type_errors.append(parameter_result.failure())
        #     else:
        #         parameters.append(parameter_result.unwrap())
        constructor = next(
            (method for method in symbol.methods if method.name == "__init__"), None
        )
        if constructor is not None:
            for parameter_analysis in constructor.parameters:
                if parameter_analysis.name == "self":
                    continue
                target_parameter_default = _find_parameter(
                    variable_name=parameter_analysis.name, default=default
                )
                parameter_result = _build_helper_function_parameter_analysis(
                    parameter_analysis=parameter_analysis,
                    identity=constructor.identity,
                    default=target_parameter_default,
                )
                if isinstance(parameter_result, Failure):
                    type_errors.append(parameter_result.failure())
                else:
                    existing_parameter = next(
                        (
                            registered
                            for registered in parameters
                            if registered.name == parameter_analysis.name
                        ),
                        None,
                    )
                    if existing_parameter is None:
                        parameters.append(parameter_result.unwrap())

    if len(type_errors) > 0:
        return Failure(tuple(type_errors))

    return Success(
        HelperInventoryItem(
            target_identity=symbol.identity,
            function_name=_build_helper_name_from_class_name(symbol.name),
            parameters=tuple(parameters),
        )
    )


def _find_model_default(
    symbol: ClassAnalysis, defaults: ModelDefaults | None
) -> ModelDefault | None:
    if defaults is None:
        return None
    return next(
        (default for default in defaults.models if default.symbol_name == symbol.name),
        None,
    )


def collect_model_helper_inventory(
    project: ProjectContext,
    workspace: WorkspaceContext,
) -> Result[tuple[HelperInventoryItem, ...], GyomuTestError | ProjectInventoryError]:
    inventories: list[HelperInventoryItem] = []
    error_files: list[FileInventoryError] = []
    for file in project.included_files:
        missing_annotations: list[MissingTypeAnnotation] = []

        file_result = load_file_analysis_context(
            project,
            file,
            option=AnalysisOption(no_check_cache=True),
        )
        if isinstance(file_result, Failure):
            return file_result.alt(
                lambda error: GyomuTestError(message="fail to load source").chain(error)
            )
        file_analysis = file_result.unwrap()

        config_request = build_config_request(
            file_analysis=file_analysis, project_context=project
        )
        default_config_result = retrieve_config(request=config_request)
        if isinstance(default_config_result, Failure):
            return default_config_result.alt(
                lambda error: GyomuTestError(message="fail to retrieve ")
            )
        default_config = default_config_result.unwrap()

        for symbol in file_analysis.analysis.symbols:
            model_kind_result = _get_model_kind(
                symbol, file_analysis.analysis, workspace
            )
            if isinstance(model_kind_result, Failure):
                return model_kind_result.alt(
                    lambda error: GyomuTestError(
                        message="fail to check if symbol is target helper fucntion",
                    ).chain(error)
                )
            model_kind = model_kind_result.unwrap()
            if model_kind is not None:
                assert isinstance(symbol, ClassAnalysis)
                class_hierarchy_result = collect_class_hierarchy(
                    cls=symbol,
                    module=file_analysis.analysis,
                    workspace=workspace,
                    is_base_first=True,
                )
                if isinstance(class_hierarchy_result, Failure):
                    return class_hierarchy_result.alt(
                        lambda error: GyomuTestError(
                            message="fail to analyze class hierarchy"
                        ).chain(error)
                    )
                target_default = _find_model_default(
                    symbol=symbol, defaults=default_config
                )
                inventory_result = _build_model_helper_inventory_item(
                    symbol=symbol,
                    collections_sorted_base_first=class_hierarchy_result.unwrap(),
                    model_kind=model_kind,
                    default=target_default,
                )
                if isinstance(inventory_result, Failure):
                    missing_annotations.extend(inventory_result.failure())
                else:
                    inventories.append(inventory_result.unwrap())

        if len(missing_annotations) > 0:
            error_files.append(
                FileInventoryError(
                    project_relative_path=file,
                    missing_annotations=tuple(missing_annotations),
                    reference_errors=tuple(),
                )
            )
    if len(error_files) > 0:
        return Failure(
            ProjectInventoryError(
                message="type is missing in managed source codes",
                project_name=project.config.name,
                project_root=project.project_root,
                error_files=tuple(error_files),
                duplicates=tuple(),
            )
        )

    return Success(tuple(inventories))
