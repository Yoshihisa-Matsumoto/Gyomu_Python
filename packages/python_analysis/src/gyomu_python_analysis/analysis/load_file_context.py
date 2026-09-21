from gyomu_schema.option.analysis import AnalysisOption
from gyomu_schema.schemas.python.file_analysis import (
    FileAnalysisContext,
)
from gyomu_schema.schemas.python.types import ProjectRelativePath
from returns.result import Failure, Result, Success

from gyomu_python_analysis.analysis.get_module import get_module_analysis
from gyomu_python_analysis.analysis.metadata import create_file_analysis_metadata
from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_python_analysis.project.context import ProjectContext


def load_file_analysis_context(
    context: ProjectContext,
    file_path: ProjectRelativePath,
    file_hash: str | None = None,
    option: AnalysisOption | None = None,
) -> Result[FileAnalysisContext, AnalysisError]:
    module_analysis_result = get_module_analysis(context, file_path, file_hash, option)
    if isinstance(module_analysis_result, Failure):
        return module_analysis_result
    module_analysis = module_analysis_result.unwrap()
    metadata = create_file_analysis_metadata(module_analysis)

    return Success(
        FileAnalysisContext(
            metadata=metadata,
            analysis=module_analysis,
        )
    )
