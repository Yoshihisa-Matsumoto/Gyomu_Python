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

from gyomu_python_analysis.error.resolve import ResolveError
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_python_analysis.resolve.models import ResolvedReference


def resolve_reference_file_analysis_context(
    reference: ResolvedReference,
    workspace: WorkspaceContext,
) -> Result[FileAnalysisContext | None, ResolveError]:
    if reference.import_analysis is None:
        return Success(None)

    return (
        workspace.find_file_analysis_context_by_module_path(reference.module_path)
        .alt(
            lambda error: ResolveError(
                message="fail to find file analysis context",
                reference=reference.module_path,
            ).chain(error)
        )
        .bind(lambda result: Success(result[0] if result is not None else None))
    )


def resolve_referenced_symbol(
    reference: ResolvedReference,
    file_analysis_context: FileAnalysisContext,
) -> Result[SymbolAnalysis | None, ResolveError]:
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


def resolve_reference_symbol(
    reference: ResolvedReference,
    workspace: WorkspaceContext,
) -> Result[SymbolAnalysis | None, ResolveError]:
    module_result = resolve_reference_file_analysis_context(reference, workspace)
    if isinstance(module_result, Failure):
        return module_result
    file_analysis_context = module_result.unwrap()
    if file_analysis_context is None:
        return Success(None)
    return resolve_referenced_symbol(
        reference=reference, file_analysis_context=file_analysis_context
    )
