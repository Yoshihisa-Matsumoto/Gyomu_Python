from gyomu_python_analysis.analysis.load_file_context import load_file_analysis_context
from gyomu_python_analysis.analysis.resolve.reference import resolve_reference
from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_python_analysis.project.context import ProjectContext
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

from gyomu_test.helper.inventory.naming import (
    _build_class_name_from_helper_name,
)


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
    target_reference = resolve_reference(return_type.text, module)
    if target_reference is None or target_reference.import_analysis is None:
        return None
    symbol_id = target_reference.import_analysis.get_symbol_id()
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
