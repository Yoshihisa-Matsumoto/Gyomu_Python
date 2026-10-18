import re

from gyomu_python_analysis.analysis.load_file_context import load_file_analysis_context
from gyomu_python_analysis.analysis.query import find_import_by_local_name
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
from gyomu_schema.schemas.python.function_analysis import FunctionAnalysis
from gyomu_schema.schemas.python.module import ModuleAnalysis
from gyomu_schema.schemas.python.parameter import ParameterAnalysis
from gyomu_schema.schemas.python.symbol import SymbolAnalysis
from gyomu_schema.schemas.python.type.type_analysis import TypeAnalysis
from gyomu_schema.schemas.python.types import (
    DeclarationId,
    DeclarationIdentity,
    ProjectRelativePath,
)
from gyomu_schema.schemas.testing.helper import HelperInventoryItem, ParameterInfo
from returns.result import Failure, Result, Success


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


def _build_helper_name_from_class_name(class_name: str) -> str:
    snake_case = re.sub(
        r"([A-Z]+)([A-Z][a-z])",
        r"\1_\2",
        class_name,
    )
    snake_case = re.sub(
        r"([a-z0-9])([A-Z])",
        r"\1_\2",
        snake_case,
    )
    return f"create_{snake_case.lower()}"


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


def _build_class_name_from_helper_name(function_name: str) -> str:
    name = function_name.removeprefix("create_")
    leading_underscores = len(name) - len(name.lstrip("_"))
    parts = [part.capitalize() for part in name.split("_") if part]

    return "_" * leading_underscores + "".join(parts)


def _is_helper_function_candidate(
    symbol: SymbolAnalysis,
    module: ModuleAnalysis,
) -> Result[bool, AnalysisError]:
    if not isinstance(symbol, FunctionAnalysis):
        return Success(False)
    func = symbol
    if not func.name.startswith("create_"):
        return Success(False)
    if func.return_type is None:
        return Success(False)

    target_class_name = _build_class_name_from_helper_name(func.name)

    if target_class_name == func.return_type.text:
        return Success(True)

    return Success(False)


def _build_helper_function_parameter_from_function(
    param: ParameterAnalysis,
) -> ParameterInfo:
    assert param.type is not None
    return ParameterInfo(name=param.name, parameter_type=param.type)


def _get_function_declaration_identity(
    return_type: TypeAnalysis, module: ModuleAnalysis
) -> DeclarationIdentity | None:
    # normalized_name = normalize_reference_name(
    #     module.imports,
    #     return_type.text,
    # )
    target_import = find_import_by_local_name(return_type.text, module)
    if target_import is None:
        return None
    symbol_id = target_import.get_symbol_id()
    if symbol_id is None:
        return None

    return DeclarationIdentity(
        symbol_id=symbol_id,
        declaration_id=DeclarationId("."),
    )


def _build_helper_inventory_item_from_function(
    symbol: FunctionAnalysis, module: ModuleAnalysis
) -> HelperInventoryItem:
    assert symbol.return_type is not None
    id = _get_function_declaration_identity(symbol.return_type, module)
    assert id is not None

    return HelperInventoryItem(
        function_name=symbol.name,
        parameters=tuple(
            [
                _build_helper_function_parameter_from_function(param)
                for param in symbol.parameters
            ]
        ),
        target_identity=id,
    )


def collect_existing_helper_inventory(
    root: ProjectContext, target_project: ProjectContext
) -> Result[tuple[HelperInventoryItem, ...], AnalysisError]:
    inventories: list[HelperInventoryItem] = []
    file_path = ProjectRelativePath(
        target_project.config.path / "test_support" / "helpers.py"
    )
    file_result = load_file_analysis_context(root, file_path)
    if isinstance(file_result, Failure):
        return file_result
    file_analysis = file_result.unwrap()
    for symbol in file_analysis.analysis.symbols:
        helper_candidate_result = _is_helper_function_candidate(
            symbol, file_analysis.analysis
        )
        if isinstance(helper_candidate_result, Failure):
            return helper_candidate_result
        if not helper_candidate_result.unwrap():
            continue

        assert isinstance(symbol, FunctionAnalysis)
        inventories.append(
            _build_helper_inventory_item_from_function(
                symbol=symbol, module=file_analysis.analysis
            )
        )

    return Success(tuple(inventories))
