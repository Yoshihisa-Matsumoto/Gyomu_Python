from dataclasses import dataclass
from enum import Enum

from gyomu_schema.schemas.python.types import WorkspaceRelativePath
from gyomu_schema.schemas.types import FullPath

from gyomu_python_analysis.project.context import PyProjectConfig


@dataclass
class WorkspaceConfig:
    """Defines configuration settings for a workspace, including path, name,
    description, and formatter line length.
    """

    path: FullPath
    """The full path of the workspace."""

    name: str | None
    """The optional name of the workspace."""

    description: str | None
    """The optional description of the workspace."""

    formatter_line_length: int
    """The line length limit configured for code formatting."""


@dataclass(frozen=True)
class WorkspaceProject:
    """Represents a project within a workspace, defined by its path and pyproject
    configuration.
    """

    path: WorkspaceRelativePath
    """The workspace-relative path of the project."""

    config: PyProjectConfig
    """The pyproject configuration associated with the project."""


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
