from gyomu_schema.schemas.python.module import ModuleAnalysis
from gyomu_schema.schemas.python.types import PythonPath
from gyomu_schema.utility.returns import from_sync
from returns.result import Failure, Result

from gyomu_python_analysis.analysis.extract.symbols import extract_symbols
from gyomu_python_analysis.analysis.load import load_module
from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_python_analysis.project.context import ProjectContext


def load_module_analysis(
    context: ProjectContext, module_path: PythonPath
) -> Result[ModuleAnalysis, AnalysisError]:
    source_file_result = load_module(context, module_path)

    if isinstance(source_file_result, Failure):
        return source_file_result

    source_file = source_file_result.unwrap()

    def analyze_module() -> ModuleAnalysis:
        source_full_path = context.project_root / context.source_root / source_file.path
        source_lines = source_full_path.read_text(encoding="utf-8").splitlines()
        symbols = extract_symbols(source_file=source_file, source_lines=source_lines)
        return ModuleAnalysis(
            path=source_file.path,
            imports=symbols.imported,
            symbols=symbols.symbols,
            name=source_file.module.name,
            docstring=None,
        )

    return from_sync(
        analyze_module,
        build_error=lambda e: AnalysisError(
            message="fail to analyze module",
            file_path=module_path,
            phase="symbol-extract",
            context="gyomu_python_analysis.analysis.load_sourde_file",
        ).chain(e),
    )
