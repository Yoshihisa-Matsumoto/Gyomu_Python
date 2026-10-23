from dataclasses import dataclass
from pathlib import Path

from gyomu_infra.filesystem.file_io import read_source_text
from gyomu_python_analysis.analysis.load_file_context import load_file_analysis_context
from gyomu_python_analysis.analysis.resolve.reference import resolve_reference
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.option.analysis import AnalysisOption
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
from gyomu_schema.schemas.testing.helper import (
    ExistingHelperInventoryItem,
    HelperFileInventory,
    ParameterInfo,
)
from gyomu_schema.schemas.types import FullPath
from returns.result import Failure, Result, Success

from gyomu_test.error.inventory import (
    DuplicateHelper,
    FileInventoryError,
    FunctionInformation,
    InvalidReference,
    MissingTypeAnnotation,
    ProjectInventoryError,
)
from gyomu_test.error.test import TestError
from gyomu_test.helper.inventory.naming import (
    _build_class_name_from_helper_name,
)


@dataclass(frozen=True)
class HelperFunctionCandidate:
    function: FunctionAnalysis
    target_identity: DeclarationIdentity


def _get_helper_function_candidate(
    symbol: SymbolAnalysis,
    module: ModuleAnalysis,
) -> Result[HelperFunctionCandidate | None, MissingTypeAnnotation | InvalidReference]:
    if not isinstance(symbol, FunctionAnalysis):
        return Success(None)
    func = symbol
    if not func.name.startswith("create_"):
        return Success(None)
    if func.return_type is None:
        return Failure(MissingTypeAnnotation(identity=symbol.identity))

    target_class_name = _build_class_name_from_helper_name(func.name)

    if target_class_name != func.return_type.text:
        return Success(None)

    declaration_identity_result = _get_function_declaration_identity(
        func, func.return_type, module
    )
    if isinstance(declaration_identity_result, Failure):
        return declaration_identity_result

    return Success(
        HelperFunctionCandidate(
            function=func, target_identity=declaration_identity_result.unwrap()
        )
    )


def _build_helper_function_parameter_from_function(
    function_symbol_id: SymbolId,
    param: ParameterAnalysis,
) -> Result[ParameterInfo, MissingTypeAnnotation]:
    if param.type is None:
        return Failure(
            MissingTypeAnnotation(
                identity=DeclarationIdentity(
                    symbol_id=function_symbol_id,
                    declaration_id=DeclarationId(f".::{param.name}"),
                )
            )
        )
    return Success(ParameterInfo(name=param.name, parameter_type=param.type))


def _get_function_declaration_identity(
    func: FunctionAnalysis, return_type: TypeAnalysis, module: ModuleAnalysis
) -> Result[DeclarationIdentity, InvalidReference]:
    # normalized_name = normalize_reference_name(
    #     module.imports,
    #     return_type.text,
    # )
    target_reference = resolve_reference(return_type.text, module)
    if target_reference is None or target_reference.import_analysis is None:
        return Failure(
            InvalidReference(identity=func.identity, reference=return_type.text)
        )
    symbol_id = target_reference.import_analysis.get_symbol_id()
    if symbol_id is None:
        return Failure(
            InvalidReference(identity=func.identity, reference=return_type.text)
        )

    return Success(
        DeclarationIdentity(
            symbol_id=symbol_id,
            declaration_id=DeclarationId("."),
        )
    )


def _build_helper_inventory_item_from_function(
    helper_function_candidate: HelperFunctionCandidate,
    module: ModuleAnalysis,
) -> Result[
    ExistingHelperInventoryItem,
    tuple[MissingTypeAnnotation, ...],
]:
    parameters: list[ParameterInfo] = []
    type_errors: list[MissingTypeAnnotation] = []
    assert helper_function_candidate.function.return_type is not None

    for param in helper_function_candidate.function.parameters:
        parameter_result = _build_helper_function_parameter_from_function(
            function_symbol_id=helper_function_candidate.function.identity.symbol_id,
            param=param,
        )
        if isinstance(parameter_result, Failure):
            type_errors.append(parameter_result.failure())
        else:
            parameters.append(parameter_result.unwrap())

    if len(type_errors) > 0:
        return Failure(tuple(type_errors))

    return Success(
        ExistingHelperInventoryItem(
            function_name=helper_function_candidate.function.name,
            parameters=tuple(parameters),
            target_identity=helper_function_candidate.target_identity,
            location=helper_function_candidate.function.location,
        )
    )


def _add_inventory_summary(
    file: ProjectRelativePath,
    helper_candidate: HelperFunctionCandidate,
    inventory_summaries: dict[DeclarationIdentity, list[FunctionInformation]],
) -> None:
    if helper_candidate.target_identity not in inventory_summaries:
        inventory_summaries[helper_candidate.target_identity] = []

    inventory_summaries[helper_candidate.target_identity].append(
        FunctionInformation(
            function_name=helper_candidate.function.name, file_path=file
        )
    )


def collect_existing_helper_inventory(
    root: ProjectContext,
    target_project: ProjectContext,
    files: tuple[ProjectRelativePath, ...] = (
        ProjectRelativePath(Path("test_support/helpers.py")),
    ),
) -> Result[
    tuple[HelperFileInventory, ...],
    TestError | ProjectInventoryError,
]:

    error_files: list[FileInventoryError] = []
    file_inventories: list[HelperFileInventory] = []
    inventory_summaries: dict[DeclarationIdentity, list[FunctionInformation]] = {}

    for file in files:
        inventories: list[ExistingHelperInventoryItem] = []
        missing_annotations: list[MissingTypeAnnotation] = []
        reference_errors: list[InvalidReference] = []
        file_path = ProjectRelativePath(target_project.config.path / file)
        file_result = load_file_analysis_context(
            root, file_path, option=AnalysisOption(no_check_cache=True)
        )
        if isinstance(file_result, Failure):
            return file_result.alt(
                lambda error: TestError(message="fail to analyze file").chain(error)
            )
        file_analysis = file_result.unwrap()
        for symbol in file_analysis.analysis.symbols:
            helper_candidate_result = _get_helper_function_candidate(
                symbol, file_analysis.analysis
            )
            if isinstance(helper_candidate_result, Failure):
                error = helper_candidate_result.failure()
                if isinstance(error, MissingTypeAnnotation):
                    missing_annotations.append(error)
                else:
                    reference_errors.append(error)
                continue
            helper_candidate = helper_candidate_result.unwrap()
            if not helper_candidate:
                continue

            assert isinstance(symbol, FunctionAnalysis)
            inventory_result = _build_helper_inventory_item_from_function(
                helper_function_candidate=helper_candidate,
                module=file_analysis.analysis,
            )
            if isinstance(inventory_result, Failure):
                missing_annotations.extend(inventory_result.failure())
            else:
                _add_inventory_summary(
                    file=file,
                    helper_candidate=helper_candidate,
                    inventory_summaries=inventory_summaries,
                )
                inventories.append(inventory_result.unwrap())

        if missing_annotations or reference_errors:
            error_files.append(
                FileInventoryError(
                    project_relative_path=file_path,
                    missing_annotations=tuple(missing_annotations),
                    reference_errors=tuple(reference_errors),
                )
            )

        else:
            source_full_path = FullPath(target_project.project_root / file)
            read_result = read_source_text(source_full_path)
            if isinstance(read_result, Failure):
                return read_result.alt(
                    lambda error: TestError(message="fail to read source").chain(error)
                )
            source = read_result.unwrap()
            source_lines = tuple(source.splitlines(keepends=True))
            file_inventories.append(
                HelperFileInventory(
                    file_path=file, items=tuple(inventories), source_lines=source_lines
                )
            )

    duplicates = tuple(
        DuplicateHelper(target_identity=identity, functions=tuple(functions))
        for identity, functions in inventory_summaries.items()
        if len(functions) > 1
    )
    if len(error_files) > 0 or len(duplicates):
        return Failure(
            ProjectInventoryError(
                message="type is missing in helper functions",
                project_name=target_project.config.name,
                project_root=target_project.project_root,
                error_files=tuple(error_files),
                duplicates=duplicates,
            )
        )

    return Success(tuple(file_inventories))
