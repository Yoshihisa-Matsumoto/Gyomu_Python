from dataclasses import dataclass

from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import WorkspaceProject
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.schemas.snapshot.types import ProjectSnapshot
from gyomu_schema.schemas.types import FullPath
from pydantic import BaseModel, Field


class FileFilter(BaseModel):
    """File filter pattern configuration.

    Represents a file filter pattern configuration.
    """

    pattern: str
    """File path matching pattern.

    The file path matching pattern.
    """


class SnapshotTargetOption(BaseModel):
    """Snapshot target selection options.

    Represents options for selecting snapshot targets.
    """

    all: bool = Field(default=False)
    """Whether to target all files.

    Whether to target all files.
    """
    file_filter: FileFilter | None = Field(default=None)
    """Optional file filter.

    Optional file filter criteria.
    """


class DocstringExecutionOption(BaseModel):
    """Docstring execution options.

    Represents execution options for docstring generation.
    """

    enabled: bool = Field(default=True)
    """Whether docstring generation is enabled.

    Whether docstring generation is enabled.
    """
    log_keyword: str | None = Field(default=None)
    """Optional log keyword.

    Optional keyword to trigger logging.
    """


class SnapshotActionOption(BaseModel):
    """Snapshot action configuration options.

    Represents options for snapshot actions such as docstring generation, project
    context, and unit tests.
    """

    docstring: DocstringExecutionOption
    """Docstring execution options.

    Docstring execution options.
    """
    project_context: bool = Field(default=False)
    """Whether to include project context.

    Whether to include project context.
    """
    unit_test: bool = Field(default=False)
    """Whether to generate unit tests.

    Whether to generate unit tests.
    """


class SnapshotExecutionOption(BaseModel):
    """Snapshot execution options.

    Represents execution options for creating a snapshot, including commit settings,
    targets, and actions.
    """

    commit: bool
    """Whether to commit.

    Whether to commit the snapshot.
    """
    target: SnapshotTargetOption
    """Target options.

    Target selection options.
    """
    action: SnapshotActionOption
    """Action options.

    Action options.
    """


@dataclass(frozen=True)
class SnapshotRequest:
    """Snapshot request parameters.

    Represents a request to create a snapshot with repository path, project context, and
    execution options.
    """

    repository_root_path: FullPath
    """Repository root path.

    Root path of the repository.
    """
    project_context: ProjectContext
    """Project context.

    Project context information.
    """
    option: SnapshotExecutionOption
    """Execution options.

    Snapshot execution options.
    """
    project: WorkspaceProject
    """Workspace project.

    Workspace project.
    """


class SnapshotTarget(BaseModel):
    """Snapshot target state.

    Represents the target state of a snapshot including files, deleted files, and the
    project snapshot.
    """

    files: frozenset[ProjectRelativePath]
    """Target files.

    Set of target files.
    """
    deleted_files: frozenset[ProjectRelativePath]
    """Deleted files.

    Set of deleted files.
    """
    snapshot: ProjectSnapshot
    """Project snapshot.

    The project snapshot.
    """
