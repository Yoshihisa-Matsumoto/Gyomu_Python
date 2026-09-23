from pathlib import Path

from gyomu_infra.filesystem.file_io import read_source_text
from gyomu_schema.option.analysis import AnalysisOption
from gyomu_schema.schemas.python.module import ModuleAnalysis
from gyomu_schema.schemas.python.types import PythonPath
from gyomu_schema.utility.returns import from_sync
from returns.result import Failure, Result

from gyomu_python_analysis.analysis.analyzers.context import initialize_symbol_context
from gyomu_python_analysis.analysis.analyzers.docstring import analyze_docstring
from gyomu_python_analysis.analysis.analyzers.internal.common import (
    build_docstring_common,
)
from gyomu_python_analysis.analysis.extract.symbols import extract_symbols
from gyomu_python_analysis.analysis.load import load_module
from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_python_analysis.path.conversion import source_relative_path_to_full_path
from gyomu_python_analysis.project.context import ProjectContext


def read_source(path: Path) -> str:
    with path.open("r", encoding="utf-8", newline="") as file:
        source = file.read()

    return source.replace("\r\n", "\n").replace("\r", "\n")


def load_module_analysis(
    context: ProjectContext,
    module_path: PythonPath,
    option: AnalysisOption | None = None,
) -> Result[ModuleAnalysis, AnalysisError]:
    source_file_result = load_module(context, module_path)

    if isinstance(source_file_result, Failure):
        return source_file_result

    source_file = source_file_result.unwrap()

    def analyze_module() -> ModuleAnalysis:
        source_full_path = source_relative_path_to_full_path(source_file.path, context)
        read_result = read_source_text(source_full_path)
        if isinstance(read_result, Failure):
            raise read_result.failure()
        source_lines = read_result.unwrap().splitlines(keepends=True)

        symbols = extract_symbols(
            source_file=source_file, source_lines=source_lines, option=option
        )
        module_name = PythonPath(source_file.module.path)
        module_context = initialize_symbol_context(
            module_name=module_name, name="", source_lines=source_lines
        )
        return ModuleAnalysis(
            path=source_file.path,
            module_name=module_name,
            imports=symbols.imported,
            symbols=symbols.symbols,
            name=source_file.module.name,
            docstring=(
                analyze_docstring(
                    source_file.module.docstring,
                    doc_common=build_docstring_common(
                        source_file.module.docstring, module_context
                    ),
                    context=module_context,
                    option=option,
                )
                if source_file.module.docstring is not None
                else None
            ),
        )

    return from_sync(
        analyze_module,
        build_error=lambda e: AnalysisError(
            message="fail to analyze module",
            file_path=module_path,
            phase="symbol-extract",
            context="gyomu_python_analysis.analysis.load_module_analysis",
        ).chain(e),
    )
