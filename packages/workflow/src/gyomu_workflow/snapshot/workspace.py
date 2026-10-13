from gyomu_infra.logger import logger
from gyomu_python_analysis.analysis.workspace import (
    find_root,
    initialize_workspace_context,
)
from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_schema.schemas.types import FullPath
from returns.result import Failure, Result


def get_workspace_context(
    current_path: FullPath,
) -> Result[WorkspaceContext, AnalysisError]:

    root_result = find_root(current_path)
    if isinstance(root_result, Failure):
        logger.error_object(root_result.failure())
        return root_result
    workspace = root_result.unwrap()
    return initialize_workspace_context(workspace)
