from returns.result import Failure, Result, Success

from gyomu_workflow.snapshot.error import SnapshotRequestValidationError
from gyomu_workflow.snapshot.models import SnapshotRequest


def validate_snapshot_request(
    request: SnapshotRequest,
) -> Result[None, SnapshotRequestValidationError]:
    if request.option.target.all and not request.option.commit:
        return Failure(
            SnapshotRequestValidationError(
                code="commit_required_for_all",
                message="commit must be enabled when all is true.",
                field="option.commit",
                expected=True,
                actual=False,
            )
        )
    return Success(None)
