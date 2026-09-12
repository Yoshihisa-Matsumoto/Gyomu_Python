from gyomu_infra.filesystem.file_io import read_json, write_json
from gyomu_infra.logger import logger
from gyomu_schema.schemas.python.module import ModuleAnalysis
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.schemas.types import FullPath
from returns.result import Failure, Result, Success

from gyomu_python_analysis.analysis.load_module import load_module_analysis
from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_python_analysis.path.conversion import (
    project_relative_path_to_source_relative_path,
    source_relative_path_to_python_path,
)
from gyomu_python_analysis.project.context import ProjectContext


def get_module_analysis(
    context: ProjectContext, file_path: ProjectRelativePath
) -> Result[ModuleAnalysis, AnalysisError]:
    cache_path = _get_cache_path(context, file_path)
    if cache_path.exists():
        cache_result = read_json(cache_path, ModuleAnalysis)
        if isinstance(cache_result, Success):
            return cache_result
        else:
            message = (
                f"fail to parse ModuleAnalysis on {cache_path}, \n"
                f"error: {repr(cache_result.failure())}"
            )
            logger.error(message)

    source_relative_path = project_relative_path_to_source_relative_path(
        path=file_path, context=context
    )
    module_path = source_relative_path_to_python_path(path=source_relative_path)
    result = load_module_analysis(context, module_path)
    if isinstance(result, Success):
        write_result = write_json(cache_path, result.unwrap())
        if isinstance(write_result, Failure):
            return Failure(
                AnalysisError(
                    "fail to write ModuleAnalysis",
                    file_path=module_path,
                    phase="post-analysis",
                ).chain(write_result.failure())
            )

    return result


def _get_cache_path(
    context: ProjectContext, source_path: ProjectRelativePath
) -> FullPath:
    cache_root = context.project_root / ".gyomu" / "cache"
    return cache_root / f"{source_path}.json"
