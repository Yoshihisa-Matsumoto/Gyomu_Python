from gyomu_schema.schemas.python.class_analysis import ClassAnalysis
from gyomu_schema.schemas.python.file_analysis import FileAnalysisContext
from gyomu_schema.schemas.python.function_analysis import FunctionAnalysis
from gyomu_schema.schemas.python.symbol import SymbolAnalysis
from gyomu_schema.schemas.python.type_alias import TypeAliasAnalysis
from gyomu_schema.schemas.python.types import DeclarationIdentity
from gyomu_schema.schemas.python.variable import VariableAnalysis
from returns.result import Failure, Result, Success

from gyomu_python_analysis.error.resolve import ResolveError
from gyomu_python_analysis.project.workspace import WorkspaceContext


def resolve_workspace_symbol_analysis(
    declaration_identity: DeclarationIdentity,
    workspace_context: WorkspaceContext,
) -> Result[tuple[FileAnalysisContext, SymbolAnalysis] | None, ResolveError]:
    module_path = declaration_identity.get_module_name()

    find_result = workspace_context.find_file_analysis_context(
        target_identity=declaration_identity
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
