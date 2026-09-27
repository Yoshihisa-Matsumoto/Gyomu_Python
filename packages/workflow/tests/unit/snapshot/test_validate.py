from pathlib import Path

from gyomu_schema.schemas.types import FullPath
from gyomu_workflow.snapshot.error import SnapshotRequestValidationError
from gyomu_workflow.snapshot.models import (
    DocstringExecutionOption,
    SnapshotActionOption,
    SnapshotExecutionOption,
    SnapshotRequest,
    SnapshotTargetOption,
)
from gyomu_workflow.snapshot.validate import validate_snapshot_request
from returns.result import Failure, Success

from packages.python_analysis.python_analysis_test_support.helpers import (
    _create_context,
)


class TestValidateSnapshotRequest:
    def test_succeeds_when_all_is_false(self) -> None:
        request = SnapshotRequest(
            repository_root_path=FullPath(Path("/tmp")),
            project_context=_create_context(),
            option=SnapshotExecutionOption(
                commit=False,
                target=SnapshotTargetOption(
                    all=False,
                ),
                action=SnapshotActionOption(
                    docstring=DocstringExecutionOption(enabled=True)
                ),
            ),
        )

        result = validate_snapshot_request(request)

        assert result == Success(None)

    def test_fails_when_all_is_true_and_commit_is_false(self) -> None:
        request = SnapshotRequest(
            repository_root_path=FullPath(Path("/tmp")),
            project_context=_create_context(),
            option=SnapshotExecutionOption(
                commit=False,
                target=SnapshotTargetOption(
                    all=True,
                ),
                action=SnapshotActionOption(
                    docstring=DocstringExecutionOption(enabled=True)
                ),
            ),
        )

        result = validate_snapshot_request(request)

        assert isinstance(result, Failure)

        error = result.failure()

        assert isinstance(error, SnapshotRequestValidationError)
        assert error.code == "commit_required_for_all"
        assert error.message == "commit must be enabled when all is true."
        assert error.field == "option.commit"
        assert error.expected is True
        assert error.actual is False

    def test_succeeds_when_all_is_true_and_commit_is_true(self) -> None:
        request = SnapshotRequest(
            repository_root_path=FullPath(Path("/tmp")),
            project_context=_create_context(),
            option=SnapshotExecutionOption(
                commit=True,
                target=SnapshotTargetOption(
                    all=True,
                ),
                action=SnapshotActionOption(
                    docstring=DocstringExecutionOption(enabled=True)
                ),
            ),
        )

        result = validate_snapshot_request(request)

        assert result == Success(None)
