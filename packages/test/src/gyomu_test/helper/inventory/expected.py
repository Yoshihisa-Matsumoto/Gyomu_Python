from gyomu_config.file.retrieve import retrieve_config
from gyomu_python_analysis.analysis.load_file_context import load_file_analysis_context
from gyomu_python_analysis.analysis.resolve.cls import (
    collect_class_hierarchy,
    inherits_from_pydantic_basemodel,
    is_dataclass_class,
)
from gyomu_python_analysis.analysis.resolve.models import ClassResolutionCollection
from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import WorkspaceContext
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
from gyomu_schema.schemas.python.symbol import SymbolAnalysis
from gyomu_schema.schemas.testing.helper import HelperInventoryItem, ParameterInfo
from returns.result import Failure, Result, Success

from gyomu_test.error.inventory import (
    FileInventoryError,
    MissingTypeAnnotation,
    ProjectInventoryError,
)
from gyomu_test.error.test import TestError
from gyomu_test.helper.inventory.config import build_config_request
from gyomu_test.helper.inventory.naming import (
    _build_helper_name_from_class_name,
)


def _is_model_candidate(
    symbol: SymbolAnalysis,
    module: ModuleAnalysis,
    workspace: WorkspaceContext,
) -> Result[bool, AnalysisError]:
    if not isinstance(symbol, ClassAnalysis):
        return Success(False)
    cls = symbol
    if is_dataclass_class(cls, module):
        return Success(True)
    return inherits_from_pydantic_basemodel(cls, module, workspace)


def _build_helper_function_parameter(
    variable: ClassVariableAnalysis, default: Parameter | None
) -> Result[ParameterInfo, MissingTypeAnnotation]:
    if variable.type is None:
        return Failure(MissingTypeAnnotation(identity=variable.identity))
    return Success(
        ParameterInfo(name=variable.name, parameter_type=variable.type, default=default)
    )


def _find_parameter(
    variable: ClassVariableAnalysis, default: ModelDefault | None
) -> Parameter | None:
    if default is None:
        return None
    return next(
        (param.value for param in default.parameters if param.name == variable.name),
        None,
    )


def _build_model_helper_inventory_item(
    symbol: ClassAnalysis,
    collections_sorted_base_first: ClassResolutionCollection,
    default: ModelDefault | None,
) -> Result[
    HelperInventoryItem,
    tuple[MissingTypeAnnotation, ...],
]:

    parameters: list[ParameterInfo] = []
    type_errors: list[MissingTypeAnnotation] = []
    for resolved in collections_sorted_base_first.resolved():
        for param in resolved.symbol.variables:
            target_parameter_default = _find_parameter(variable=param, default=default)
            parameter_result = _build_helper_function_parameter(
                param, default=target_parameter_default
            )
            if isinstance(parameter_result, Failure):
                type_errors.append(parameter_result.failure())
            else:
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
        (default for default in defaults.models if default.class_name == symbol.name),
        None,
    )


def collect_model_helper_inventory(
    project: ProjectContext,
    workspace: WorkspaceContext,
) -> Result[tuple[HelperInventoryItem, ...], TestError | ProjectInventoryError]:
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
                lambda error: TestError(message="fail to load source").chain(error)
            )
        file_analysis = file_result.unwrap()

        config_request = build_config_request(
            file_analysis=file_analysis, project_context=project
        )
        default_config_result = retrieve_config(request=config_request)
        if isinstance(default_config_result, Failure):
            return default_config_result.alt(
                lambda error: TestError(message="fail to retrieve ")
            )
        default_config = default_config_result.unwrap()

        for symbol in file_analysis.analysis.symbols:
            in_scope_result = _is_model_candidate(
                symbol, file_analysis.analysis, workspace
            )
            if isinstance(in_scope_result, Failure):
                return in_scope_result.alt(
                    lambda error: TestError(
                        message="fail to check if symbol is target helper fucntion",
                    ).chain(error)
                )
            if in_scope_result.unwrap():
                assert isinstance(symbol, ClassAnalysis)
                class_hierarchy_result = collect_class_hierarchy(
                    cls=symbol,
                    module=file_analysis.analysis,
                    workspace=workspace,
                    is_base_first=True,
                )
                if isinstance(class_hierarchy_result, Failure):
                    return class_hierarchy_result.alt(
                        lambda error: TestError(
                            message="fail to analyze class hierarchy"
                        ).chain(error)
                    )
                target_default = _find_model_default(
                    symbol=symbol, defaults=default_config
                )
                inventory_result = _build_model_helper_inventory_item(
                    symbol=symbol,
                    collections_sorted_base_first=class_hierarchy_result.unwrap(),
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
