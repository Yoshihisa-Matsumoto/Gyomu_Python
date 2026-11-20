from dataclasses import dataclass

from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_test.helper.defaults.requirements import (
    MissingParameterDefault,
)


@dataclass(frozen=True)
class DefaultTypeParameterContext:
    parameter: MissingParameterDefault
    workspace_context: WorkspaceContext
    workspace_root_project_context: ProjectContext
    project_context: ProjectContext
