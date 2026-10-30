from gyomu_schema.option.analysis import AnalysisOption
from gyomu_schema.schemas.python.file_analysis import FileAnalysisContext
from gyomu_schema.schemas.python.types import (
    DeclarationIdentity,
    PythonPath,
)
from returns.result import Failure, Result, Success

from gyomu_python_analysis.analysis.load_file_context import load_file_analysis_context
from gyomu_python_analysis.error.resolve import ResolveError
from gyomu_python_analysis.path.conversion import (
    python_path_to_source_project_relative_path,
)
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import WorkspaceContext


class FileAnalysisCache:
    def __init__(self, workspace_context: WorkspaceContext) -> None:
        self._workspace_context = workspace_context
        self._cache: dict[PythonPath, FileAnalysisContext] = {}

    def get_file_analysis_context(
        self,
        project_context: ProjectContext,
        identity: DeclarationIdentity,
    ) -> Result[FileAnalysisContext, ResolveError]:
        python_path = identity.get_module_name()
        context = self._cache.get(python_path)
        if context is not None:
            return Success(context)
        file_path = python_path_to_source_project_relative_path(
            path=python_path, context=project_context
        )
        context_result = load_file_analysis_context(
            context=project_context,
            file_path=file_path,
            option=AnalysisOption(no_check_cache=True),
        )
        if isinstance(context_result, Failure):
            return context_result.alt(
                lambda error: ResolveError(
                    message="fail to load file analysis context", reference=file_path
                ).chain(error)
            )
        return Success(self._cache.setdefault(python_path, context_result.unwrap()))
