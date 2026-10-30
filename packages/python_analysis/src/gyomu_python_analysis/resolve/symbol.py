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
