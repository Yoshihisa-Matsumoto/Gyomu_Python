from gyomu_infra.filesystem.file_io import read_json, write_json
from gyomu_infra.logger import logger
from gyomu_schema.option.analysis import AnalysisOption
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
    context: ProjectContext,
    file_path: ProjectRelativePath,
    file_hash: str | None = None,
    option: AnalysisOption | None = None,
) -> Result[ModuleAnalysis, AnalysisError]:
    """Get module analysis for a given file path.

    Analyzes a Python module, leveraging cached results when available.

    Args:
        context (ProjectContext): The project context.
        file_path (ProjectRelativePath): The relative path of the file to analyze.
        file_hash (str | None): Optional file hash for cache validation.
        option (AnalysisOption | None): Optional analysis options.

    Returns:
        Result[ModuleAnalysis, AnalysisError]: A Result containing the ModuleAnalysis on
            success or AnalysisError on failure.
    """

    cache_path = _get_cache_path(context, file_path)

    if (option is None or not option.no_check_cache) and cache_path.exists():
        cache_result = read_json(cache_path, ModuleAnalysis)

        if isinstance(cache_result, Success):
            if (
                file_hash is None
                or file_hash == cache_result.unwrap().name == file_hash
            ):
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
    result = load_module_analysis(context, module_path, option)
    if isinstance(result, Success):
        write_result = write_json(cache_path, result.unwrap(), ModuleAnalysis)
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
    """Get the cache file path for a source file.

    Computes the full path for a module's analysis cache file.

    Args:
        context (ProjectContext): The project context.
        source_path (ProjectRelativePath): The source path relative to the project.

    Returns:
        FullPath: The full path to the cache file.
    """
    cache_root = context.project_root / ".gyomu" / "cache"
    return cache_root / f"{source_path}.json"
