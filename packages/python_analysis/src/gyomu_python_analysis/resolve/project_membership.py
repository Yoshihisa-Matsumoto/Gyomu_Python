from gyomu_schema.schemas.python.file_analysis import FileAnalysisContext
from returns.result import Failure, Result, Success

from gyomu_python_analysis.analysis.initialize import (
    find_package_roots_from_workspace_project,
)
from gyomu_python_analysis.error.resolve import ResolveError
from gyomu_python_analysis.project.context import (
    PackageRoot,
    ProjectContext,
    WorkspaceProject,
)
from gyomu_python_analysis.project.workspace import WorkspaceContext, WorkspaceRoot


def is_file_in_project(
    file_context: FileAnalysisContext,
    project_context: ProjectContext,
) -> bool:
    return _is_file_in_project_roots(
        file_context=file_context, package_roots=project_context.package_roots
    )


def find_workspace_project(
    file_context: FileAnalysisContext,
    workspace_root: WorkspaceRoot,
    workspace_context: WorkspaceContext,
) -> Result[WorkspaceProject, ResolveError]:
    for workspace_project in workspace_context.projects:
        if _is_file_in_workspace_project(
            file_context=file_context,
            workspace_root=workspace_root,
            workspace_project=workspace_project,
        ):
            return Success(workspace_project)

    return Failure(
        ResolveError(
            message=(
                "Could not find the workspace project containing "
                f"module '{file_context.analysis.module_name}'."
            ),
            reference=file_context.analysis.module_name,
        )
    )


def _is_file_in_project_roots(
    file_context: FileAnalysisContext, package_roots: tuple[PackageRoot, ...]
) -> bool:
    module_name = file_context.analysis.module_name

    return any(
        module_name == root.module_name
        or module_name.startswith(f"{root.module_name}.")
        for root in package_roots
    )


def _is_file_in_workspace_project(
    file_context: FileAnalysisContext,
    workspace_root: WorkspaceRoot,
    workspace_project: WorkspaceProject,
) -> bool:
    package_roots = find_package_roots_from_workspace_project(
        workspace_path=workspace_root.path, project=workspace_project
    )
    return _is_file_in_project_roots(
        file_context=file_context, package_roots=package_roots
    )
