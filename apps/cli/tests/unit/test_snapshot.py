from unittest.mock import AsyncMock, MagicMock

from gyomu_cli.snapshot import run_snapshot_request
from gyomu_schema.error.base import BaseError
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.concept.test_support.helpers import build_workspace_context
from packages.python_analysis.test_support.helpers import (
    create_workspace_project,
)
from packages.workflow.test_support.helper import create_snapshot_execution_option


class TestRunSnapshotRequest:
    def test_returns_success_when_snapshot_succeeds(
        self,
        mocker: MockerFixture,
    ) -> None:
        workspace_context = build_workspace_context()
        project = create_workspace_project()
        option = create_snapshot_execution_option()
        request = MagicMock()

        mocker.patch(
            "gyomu_cli.snapshot.translate_snapshot_request",
            return_value=request,
        )
        validate_mock = mocker.patch(
            "gyomu_cli.snapshot.validate_snapshot_request",
            return_value=Success(None),
        )
        run_mock = mocker.patch(
            "gyomu_cli.snapshot.run_snapshot",
            new_callable=AsyncMock,
            return_value=Success(None),
        )

        result = run_snapshot_request(workspace_context, project, option)

        assert isinstance(result, Success)
        assert result.unwrap() is None
        validate_mock.assert_called_once_with(request)
        run_mock.assert_awaited_once_with(request)

    def test_returns_failure_when_validation_fails(
        self,
        mocker: MockerFixture,
    ) -> None:
        workspace_context = build_workspace_context()
        project = create_workspace_project()
        option = create_snapshot_execution_option()
        request = MagicMock()
        error = MagicMock(spec=BaseError)

        mocker.patch(
            "gyomu_cli.snapshot.translate_snapshot_request",
            return_value=request,
        )
        mocker.patch(
            "gyomu_cli.snapshot.validate_snapshot_request",
            return_value=Failure(error),
        )
        run_mock = mocker.patch("gyomu_cli.snapshot.asyncio.run")
        logger_mock = mocker.patch("gyomu_cli.snapshot.logger.error_object")
        run_snapshot_mock = mocker.patch(
            "gyomu_cli.snapshot.run_snapshot",
            new_callable=AsyncMock,
        )
        run_mock = mocker.patch("gyomu_cli.snapshot.asyncio.run")

        result = run_snapshot_request(workspace_context, project, option)

        assert isinstance(result, Failure)
        assert result.failure() is error
        logger_mock.assert_called_once_with(error)
        run_mock.assert_not_called()
        run_snapshot_mock.assert_not_called()
        run_mock.assert_not_called()

    def test_returns_failure_when_snapshot_fails(
        self,
        mocker: MockerFixture,
    ) -> None:
        workspace_context = build_workspace_context()
        project = create_workspace_project()
        option = create_snapshot_execution_option()
        request = MagicMock()
        error = MagicMock(spec=BaseError)

        mocker.patch(
            "gyomu_cli.snapshot.translate_snapshot_request",
            return_value=request,
        )
        mocker.patch(
            "gyomu_cli.snapshot.validate_snapshot_request",
            return_value=Success(None),
        )
        mocker.patch(
            "gyomu_cli.snapshot.run_snapshot",
            new_callable=AsyncMock,
            return_value=Failure(error),
        )

        logger_mock = mocker.patch("gyomu_cli.snapshot.logger.error_object")

        result = run_snapshot_request(workspace_context, project, option)

        assert isinstance(result, Failure)
        assert result.failure() is error
        logger_mock.assert_called_once_with(error, depth=6)
