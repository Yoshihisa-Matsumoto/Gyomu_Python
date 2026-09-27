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
    """Converts a project-relative path to a source-relative path using the project
    context.
    """
    return SourceRelativePath(path.relative_to(context.source_root))


def source_relative_path_to_project_relative_path(
    path: SourceRelativePath,
    context: ProjectContext,
) -> ProjectRelativePath:
    """Converts a source-relative path to a project-relative path using the project
    context.
    """
    return ProjectRelativePath(context.source_root / path)


def source_relative_path_to_python_path(
    path: SourceRelativePath,
) -> PythonPath:
    """Converts a source-relative path to a Python dotted module path."""

    if path.name == "__init__.py":
        path = SourceRelativePath(path.parent)
    else:
        path = SourceRelativePath(path.with_suffix(""))

    return PythonPath(".".join(path.parts))


def source_relative_path_to_full_path(
    path: SourceRelativePath,
    context: ProjectContext,
) -> FullPath:
    """Converts a source-relative path to a full absolute path using the project
    context.
    """
    return FullPath(context.project_root / context.source_root / path)
