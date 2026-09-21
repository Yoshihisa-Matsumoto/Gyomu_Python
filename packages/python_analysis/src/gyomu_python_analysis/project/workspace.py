from dataclasses import dataclass
from enum import Enum

from gyomu_schema.schemas.python.types import WorkspaceRelativePath
from gyomu_schema.schemas.types import FullPath

from gyomu_python_analysis.project.context import PyProjectConfig


@dataclass
class WorkspaceConfig:
    path: FullPath
    name: str | None
    description: str | None
    formatter_line_length: int


@dataclass(frozen=True)
class WorkspaceProject:
    path: WorkspaceRelativePath
    config: PyProjectConfig


@dataclass
class WorkspaceContext:
    def __init__(
        self, config: WorkspaceConfig, projects: tuple[WorkspaceProject, ...]
    ) -> None:
        self.config = config
        self.projects = projects


class WorkspaceRootKind(Enum):
    UV_WORKSPACE = "uv-workspace"
    STANDALONE_PROJECT = "standalone-project"


@dataclass(frozen=True)
class WorkspaceRoot:
    path: FullPath
    kind: WorkspaceRootKind
