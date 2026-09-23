from gyomu_infra.filesystem.file_io import delete_file
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.utility.context import caller_context
from returns.result import Result, Success

from gyomu_python_analysis.analysis.get_module import _get_cache_path
from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_python_analysis.project.context import ProjectContext


def delete_module_cache(
    project_context: ProjectContext,
    file_path: ProjectRelativePath,
) -> Result[None, AnalysisError]:
    cache_path = _get_cache_path(project_context, file_path)
    if cache_path.exists():
        context = caller_context()
        return delete_file(cache_path).alt(
            lambda error: AnalysisError(
                "fail to delete file analysis cache",
                file_path=cache_path,
                phase="analysis",
                context=context,
            ).chain(error)
        )
    return Success(None)
