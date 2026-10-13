import asyncio

from gyomu_infra.logger import logger
from gyomu_python_analysis.project.workspace import WorkspaceContext, WorkspaceProject
from gyomu_schema.error.base import BaseError
from gyomu_workflow.snapshot.models import SnapshotExecutionOption
from gyomu_workflow.snapshot.run import run_snapshot
from gyomu_workflow.snapshot.translate import translate_snapshot_request
from gyomu_workflow.snapshot.validate import validate_snapshot_request
from returns.result import Failure, Result, Success


def run_snapshot_request(
    workspace_context: WorkspaceContext,
    project: WorkspaceProject,
    option: SnapshotExecutionOption,
) -> Result[None, BaseError]:
    request = translate_snapshot_request(workspace_context, project, option)

    logger.info(
        f"commit: {request.option.commit}, "
        f"docstring:{request.option.action.docstring.enabled}, "
        f"all={request.option.target.all}"
    )
    if option.target.file_filter:
        logger.info(f"filter: {option.target.file_filter.pattern}")
    if option.action.docstring.log_keyword is not None:
        logger.info(f"log_keyword: {request.option.action.docstring.log_keyword}")

    validation_result = validate_snapshot_request(request)
    if isinstance(validation_result, Failure):
        logger.error_object(validation_result.failure())
        return validation_result

    snapshot_result = asyncio.run(run_snapshot(request))
    if isinstance(snapshot_result, Failure):
        logger.error_object(snapshot_result.failure(), depth=6)
        return snapshot_result

    return Success(None)
