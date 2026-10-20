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
    SymbolId,
)
from gyomu_schema.schemas.testing.helper import HelperInventoryItem, ParameterInfo
from returns.result import Failure, Result, Success

from gyomu_test.error.inventory import (
    FileMissingTypeAnnotation,
    MissingTypeAnnotation,
    ProjectMissingTypeAnnotationError,
)
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
    function_symbol_id: SymbolId,
    param: ParameterAnalysis,
) -> Result[ParameterInfo, MissingTypeAnnotation]:
    if param.type is None:
        return Failure(
            MissingTypeAnnotation(
                identity=DeclarationIdentity(
                    symbol_id=function_symbol_id,
                    declaration_id=DeclarationId(param.name),
                )
            )
        )
    return Success(ParameterInfo(name=param.name, parameter_type=param.type))


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
) -> Result[
    HelperInventoryItem,
    tuple[MissingTypeAnnotation, ...],
]:
    parameters: list[ParameterInfo] = []
    type_errors: list[MissingTypeAnnotation] = []
    assert symbol.return_type is not None
    id = _get_function_declaration_identity(symbol.return_type, module)
    assert id is not None

    for param in symbol.parameters:
        parameter_result = _build_helper_function_parameter_from_function(
            function_symbol_id=symbol.identity.symbol_id, param=param
        )
        if isinstance(parameter_result, Failure):
            type_errors.append(parameter_result.failure())
        else:
            parameters.append(parameter_result.unwrap())

    if len(type_errors) > 0:
        return Failure(tuple(type_errors))

    return Success(
        HelperInventoryItem(
            function_name=symbol.name,
            parameters=tuple(parameters),
            target_identity=id,
        )
    )


def collect_existing_helper_inventory(
    root: ProjectContext, target_project: ProjectContext
) -> Result[
    tuple[HelperInventoryItem, ...], AnalysisError | ProjectMissingTypeAnnotationError
]:
    inventories: list[HelperInventoryItem] = []
    error_files: list[FileMissingTypeAnnotation] = []
    files = ["helpers.py"]
    for file in files:
        missing_annotations: list[MissingTypeAnnotation] = []
        file_path = ProjectRelativePath(
            target_project.config.path / "test_support" / file
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
            inventory_result = _build_helper_inventory_item_from_function(
                symbol=symbol, module=file_analysis.analysis
            )
            if isinstance(inventory_result, Failure):
                missing_annotations.extend(inventory_result.failure())
            else:
                inventories.append(inventory_result.unwrap())

        if len(missing_annotations) > 0:
            error_files.append(
                FileMissingTypeAnnotation(
                    project_relative_path=file_path,
                    missing_annotations=tuple(missing_annotations),
                )
            )
    if len(error_files) > 0:
        return Failure(
            ProjectMissingTypeAnnotationError(
                message="type is missing in helper functions",
                project_name=target_project.config.name,
                project_root=target_project.project_root,
                error_files=tuple(error_files),
            )
        )

    return Success(tuple(inventories))
