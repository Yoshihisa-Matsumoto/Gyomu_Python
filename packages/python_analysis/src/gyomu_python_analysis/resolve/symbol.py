from gyomu_schema.schemas.python.class_analysis import ClassAnalysis
from gyomu_schema.schemas.python.file_analysis import FileAnalysisContext
from gyomu_schema.schemas.python.function_analysis import FunctionAnalysis
from gyomu_schema.schemas.python.symbol import SymbolAnalysis
from gyomu_schema.schemas.python.type_alias import TypeAliasAnalysis
from gyomu_schema.schemas.python.types import DeclarationIdentity
from gyomu_schema.schemas.python.variable import VariableAnalysis
from returns.result import Failure, Result, Success

from gyomu_python_analysis.error.resolve import ResolveError
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_python_analysis.resolve.file_analysis_cache import FileAnalysisCache


def resolve_symbol_analysis(
    declaration_identity: DeclarationIdentity,
    project_context: ProjectContext,
    file_analysis_cache: FileAnalysisCache,
) -> Result[tuple[FileAnalysisContext, SymbolAnalysis], ResolveError]:
    context_result = file_analysis_cache.get_file_analysis_context(
        project_context=project_context, identity=declaration_identity
    )
    if isinstance(context_result, Failure):
        return context_result.alt(
            lambda error: ResolveError(
                message="fail to resolve symbol",
                reference=declaration_identity.get_module_name(),
                details={"identity": declaration_identity},
            ).chain(error)
        )
    file_analysis = context_result.unwrap()

    symbol = file_analysis.metadata.symbols.get(declaration_identity)
    if symbol is not None and isinstance(
        symbol, VariableAnalysis | ClassAnalysis | FunctionAnalysis | TypeAliasAnalysis
    ):
        return Success((file_analysis, symbol))
    return Failure(
        ResolveError(
            message="symbol is not found",
            reference=declaration_identity.get_module_name(),
            details={"identity": declaration_identity},
        )
    )


def resolve_workspace_symbol_analysis(
    declaration_identity: DeclarationIdentity,
    workspace_context: WorkspaceContext,
) -> Result[tuple[FileAnalysisContext, SymbolAnalysis] | None, ResolveError]:
    module_path = declaration_identity.get_module_name()

    find_result = workspace_context.find_workspace_file_analysis_context(
        module_path=module_path
    )
    if isinstance(find_result, Failure):
        return find_result.alt(
            lambda error: ResolveError(
                "fail to find target file", reference=module_path
            ).chain(error)
        )
    record = find_result.unwrap()
    if record is not None:
        file_analysis_context, found_project = record
        symbol = file_analysis_context.metadata.symbols.get(declaration_identity)
        if symbol is None:
            return Failure(
                ResolveError(
                    "can not find symbol on the file",
                    reference=file_analysis_context.analysis.path,
                    details={
                        "project": found_project.config.name,
                        "target_symbol": declaration_identity.symbol_id,
                    },
                )
            )
        elif not isinstance(
            symbol,
            VariableAnalysis | ClassAnalysis | FunctionAnalysis | TypeAliasAnalysis,
        ):
            return Failure(
                ResolveError(
                    "target symbol is not Symbol",
                    reference=file_analysis_context.analysis.path,
                    details={
                        "project": found_project.config.name,
                        "target_identity": declaration_identity,
                    },
                )
            )
        return Success((file_analysis_context, symbol))
    else:
        return Success(None)
