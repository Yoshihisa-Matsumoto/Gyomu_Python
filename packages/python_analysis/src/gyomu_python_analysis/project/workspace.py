from dataclasses import dataclass
from enum import Enum

from gyomu_schema.schemas.python.file_analysis import FileAnalysisContext
from gyomu_schema.schemas.python.types import PythonPath
from gyomu_schema.schemas.types import FullPath
from returns.result import Failure, Result, Success

from gyomu_python_analysis.analysis.initialize import initialize_project_from_workspace
from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_python_analysis.path.conversion import (
    python_path_to_source_project_relative_path,
)
from gyomu_python_analysis.project.context import (
    ProjectContext,
    PyProjectConfig,
    WorkspaceProject,
)
from gyomu_python_analysis.resolve.load_file_context import load_file_analysis_context


@dataclass
class WorkspaceContext:
    """Encapsulates workspace context, containing the workspace configuration and its
    projects.
    """

    def __init__(
        self,
        path: FullPath,
        config: PyProjectConfig,
        projects: tuple[WorkspaceProject, ...],
    ) -> None:
        self.path = path
        self.config = config
        self.projects = projects
        self._project_indexes: dict[str, ProjectContext] = {}

    def _initialize_project_indexes(self) -> None:
        for project in self.projects:
            project_context = initialize_project_from_workspace(self.path, project)
            for package_root in project_context.package_roots:
                self._project_indexes[package_root.module_name] = project_context

    def find_workspace_file_analysis_context(
        self,
        module_path: PythonPath,
    ) -> Result[FileAnalysisContext | None, AnalysisError]:
        """Find analysis context for a module in a workspace-managed package.

        Gyomu Context: Returns Success(None) when the module's root package is not
        managed by the workspace. Returns Failure when the package is managed but
        the target module does not exist or cannot be analyzed.
        """
        if len(self._project_indexes) == 0:
            self._initialize_project_indexes()
        root_module_name = module_path.split(".")[0]
        target_package = self._project_indexes.get(root_module_name)
        if target_package is None:
            return Success(None)
        else:
            project_source_path = python_path_to_source_project_relative_path(
                path=module_path, context=target_package
            )
            if not (target_package.project_root / project_source_path).exists():
                return Failure(
                    AnalysisError(
                        message="target module not found",
                        file_path=module_path,
                        phase="workspace-discovery",
                        details={"project_name": target_package.config.name},
                    )
                )
            return load_file_analysis_context(target_package, project_source_path)


class WorkspaceRootKind(Enum):
    """Defines the kind of workspace root, such as a uv workspace or a standalone
    project.
    """

    UV_WORKSPACE = "uv-workspace"
    """Represents a uv-managed workspace root."""

    STANDALONE_PROJECT = "standalone-project"
    """Represents a standalone project root."""


@dataclass(frozen=True)
class WorkspaceRoot:
    """Represents the root directory of a workspace, including its path and root
    kind.
    """

    path: FullPath
    """The full path of the workspace root."""

    kind: WorkspaceRootKind
    """The kind of workspace root."""
