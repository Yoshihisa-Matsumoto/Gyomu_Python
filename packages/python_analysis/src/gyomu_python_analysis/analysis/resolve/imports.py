from gyomu_schema.schemas.python.class_analysis import ClassAnalysis
from gyomu_schema.schemas.python.file_analysis import FileAnalysisContext
from gyomu_schema.schemas.python.function_analysis import FunctionAnalysis
from gyomu_schema.schemas.python.symbol import SymbolAnalysis
from gyomu_schema.schemas.python.type_alias import TypeAliasAnalysis
from gyomu_schema.schemas.python.types import (
    DeclarationId,
    DeclarationIdentity,
)
from gyomu_schema.schemas.python.variable import VariableAnalysis
from returns.result import Failure, Result, Success

from gyomu_python_analysis.analysis.resolve.models import ResolvedReference
from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_python_analysis.project.workspace import WorkspaceContext

# def resolve_import_file_analysis_context(
#     target_import: ImportAnalysis, workspace: WorkspaceContext
# ) -> Result[FileAnalysisContext | None, AnalysisError]:
#     module_path = target_import.get_module_path()
#     if not module_path:
#         return Success(None)

#     return workspace.find_file_analysis_context(module_path)


def resolve_reference_file_analysis_context(
    reference: ResolvedReference,
    workspace: WorkspaceContext,
) -> Result[FileAnalysisContext | None, AnalysisError]:
    if reference.import_analysis is None:
        return Success(None)

    return workspace.find_workspace_file_analysis_context(reference.module_path)


def resolve_referenced_symbol(
    reference: ResolvedReference,
    file_analysis_context: FileAnalysisContext,
) -> Result[SymbolAnalysis | None, AnalysisError]:
    if reference.import_analysis is None:
        return Success(None)
    symbol_id = reference.symbol_id
    if symbol_id is None:
        return Success(None)

    target_symbol = file_analysis_context.metadata.symbols.get(
        DeclarationIdentity(
            symbol_id=symbol_id,
            declaration_id=DeclarationId("."),
        )
    )

    if target_symbol is None:
        return Success(None)
    if isinstance(
        target_symbol,
        (VariableAnalysis, ClassAnalysis, FunctionAnalysis, TypeAliasAnalysis),
    ):
        return Success(target_symbol)

    return Success(None)


# def resolve_imported_symbol(
#     target_import: ImportAnalysis, file_analysis_context: FileAnalysisContext
# ) -> Result[SymbolAnalysis | None, AnalysisError]:
#     symbol_id = target_import.get_symbol_id()
#     if symbol_id is None:
#         return Success(None)

#     target_symbol = file_analysis_context.metadata.symbols.get(
#         DeclarationIdentity(
#             symbol_id=symbol_id,
#             declaration_id=DeclarationId("."),
#         )
#     )

#     if target_symbol is None:
#         return Success(None)
#     if isinstance(
#         target_symbol,
#         (VariableAnalysis, ClassAnalysis, FunctionAnalysis, TypeAliasAnalysis),
#     ):
#         return Success(target_symbol)

#     return Success(None)


def resolve_reference_symbol(
    reference: ResolvedReference,
    workspace: WorkspaceContext,
) -> Result[SymbolAnalysis | None, AnalysisError]:
    module_result = resolve_reference_file_analysis_context(reference, workspace)
    if isinstance(module_result, Failure):
        return module_result
    file_analysis_context = module_result.unwrap()
    if file_analysis_context is None:
        return Success(None)
    return resolve_referenced_symbol(
        reference=reference, file_analysis_context=file_analysis_context
    )


# def resolve_import_symbol(
#     target_import: ImportAnalysis, workspace: WorkspaceContext
# ) -> Result[SymbolAnalysis | None, AnalysisError]:
#     module_result = resolve_import_file_analysis_context(target_import, workspace)
#     if isinstance(module_result, Failure):
#         return module_result
#     file_analysis_context = module_result.unwrap()
#     if file_analysis_context is None:
#         return Success(None)
#     return resolve_imported_symbol(
#         target_import=target_import, file_analysis_context=file_analysis_context
#     )
