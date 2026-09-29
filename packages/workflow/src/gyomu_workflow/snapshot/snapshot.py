from gyomu_python_analysis.snapshot.analyze import analyze_project_changes
from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.schemas.snapshot.types import ProjectSnapshot
from gyomu_schema.utility.context import caller_context
from returns.result import Failure, Result, Success

from gyomu_workflow.snapshot.models import SnapshotRequest


def update_snapshot(request: SnapshotRequest) -> Result[ProjectSnapshot, GyomuError]:
    context = caller_context()
    analysis_result = analyze_project_changes(
        repository_root_path=request.repository_root_path,
        project_context=request.project_context,
    )
    if isinstance(analysis_result, Failure):
        return analysis_result.alt(
            lambda error: GyomuError(
                message="fail to analyze project change",
                domain="snapshot",
                operation="run_actions",
                reason="external_failure",
                context=context,
            ).chain(error)
        )
    return Success(analysis_result.unwrap().current_snapshot)
