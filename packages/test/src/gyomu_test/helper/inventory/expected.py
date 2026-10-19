from gyomu_python_analysis.analysis.load_file_context import load_file_analysis_context
from gyomu_python_analysis.analysis.resolve.cls import (
    inherits_from_pydantic_basemodel,
    is_dataclass_class,
)
from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_schema.schemas.python.class_analysis import (
    ClassAnalysis,
    ClassVariableAnalysis,
)
from gyomu_schema.schemas.python.module import ModuleAnalysis
from gyomu_schema.schemas.python.symbol import SymbolAnalysis
from gyomu_schema.schemas.testing.helper import HelperInventoryItem, ParameterInfo
from returns.result import Failure, Result, Success

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
    variable: ClassVariableAnalysis,
) -> ParameterInfo:
    assert variable.type is not None
    return ParameterInfo(name=variable.name, parameter_type=variable.type)


def _build_model_helper_inventory_item(
    symbol: ClassAnalysis,
) -> HelperInventoryItem:
    return HelperInventoryItem(
        target_identity=symbol.identity,
        function_name=_build_helper_name_from_class_name(symbol.name),
        parameters=tuple(
            [_build_helper_function_parameter(param) for param in symbol.variables]
        ),
    )


def collect_model_helper_inventory(
    project: ProjectContext,
    workspace: WorkspaceContext,
) -> Result[tuple[HelperInventoryItem, ...], AnalysisError]:
    inventories: list[HelperInventoryItem] = []
    for file in project.included_files:
        file_result = load_file_analysis_context(project, file)
        if isinstance(file_result, Failure):
            return file_result
        file_analysis = file_result.unwrap()
        for symbol in file_analysis.analysis.symbols:
            in_scope_result = _is_model_candidate(
                symbol, file_analysis.analysis, workspace
            )
            if isinstance(in_scope_result, Failure):
                return in_scope_result
            if in_scope_result.unwrap():
                assert isinstance(symbol, ClassAnalysis)
                inventories.append(_build_model_helper_inventory_item(symbol))

    return Success(tuple(inventories))
