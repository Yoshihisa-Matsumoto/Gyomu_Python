from gyomu_schema.schemas.python.types import (
    ProjectRelativePath,
    PythonPath,
    SourceRelativePath,
)
from gyomu_schema.schemas.types import FullPath

from gyomu_python_analysis.project.context import ProjectContext


def project_relative_path_to_source_relative_path(
    path: ProjectRelativePath,
    context: ProjectContext,
) -> SourceRelativePath:
    return SourceRelativePath(path.relative_to(context.source_root))


def source_relative_path_to_project_relative_path(
    path: SourceRelativePath,
    context: ProjectContext,
) -> ProjectRelativePath:
    return ProjectRelativePath(context.source_root / path)


def source_relative_path_to_python_path(
    path: SourceRelativePath,
) -> PythonPath:
    if path.name == "__init__.py":
        path = SourceRelativePath(path.parent)
    else:
        path = SourceRelativePath(path.with_suffix(""))

    return PythonPath(".".join(path.parts))


def source_relative_path_to_full_path(
    path: SourceRelativePath,
    context: ProjectContext,
) -> FullPath:
    return FullPath(context.project_root / context.source_root / path)
