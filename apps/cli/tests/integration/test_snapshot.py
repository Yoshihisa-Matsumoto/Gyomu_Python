from pathlib import Path

import pytest
from gyomu_cli.main import app
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.schemas.types import FullPath
from gyomu_workflow.snapshot.models import (
    DocstringExecutionOption,
    SnapshotActionOption,
    SnapshotExecutionOption,
    SnapshotRequest,
    SnapshotTargetOption,
)
from pytest_mock import MockerFixture
from returns.result import Failure, Success
from typer.testing import CliRunner

runner = CliRunner()


@pytest.fixture
def snapshot_request(mocker: MockerFixture) -> SnapshotRequest:
    return SnapshotRequest(
        repository_root_path=FullPath(Path("/tmp")),
        project_context=mocker.Mock(spec=ProjectContext),
        option=SnapshotExecutionOption(
            commit=True,
            action=SnapshotActionOption(
                docstring=DocstringExecutionOption(enabled=True),
            ),
            target=SnapshotTargetOption(),
        ),
    )


def test_snapshot_success(mocker: MockerFixture, snapshot_request: SnapshotRequest):

    mocker.patch(
        "gyomu_cli.main.translate_snapshot_request",
        return_value=Success(snapshot_request),
    )
    mocker.patch(
        "gyomu_cli.main.validate_snapshot_request",
        return_value=Success(None),
    )
    run_snapshot = mocker.patch(
        "gyomu_cli.main.run_snapshot",
        return_value=Success(None),
    )

    result = runner.invoke(
        app,
        [
            "snapshot",
            "test-package",
            "--docstring",
            "--all",
            "--commit",
            "--log-keyword",
            "test",
        ],
    )

    assert result.exit_code == 0

    run_snapshot.assert_awaited_once_with(snapshot_request)


def test_snapshot_translate_failure(
    mocker: MockerFixture,
):
    error = GyomuError(
        message="translate failed",
        domain="test",
        operation="translate",
        reason="invalid_input",
    )

    mocker.patch(
        "gyomu_cli.main.translate_snapshot_request",
        return_value=Failure(error),
    )
    validate_snapshot_request = mocker.patch(
        "gyomu_cli.main.validate_snapshot_request",
    )
    run_snapshot = mocker.patch(
        "gyomu_cli.main.run_snapshot",
    )

    result = runner.invoke(
        app,
        [
            "snapshot",
            "test-package",
        ],
    )

    assert result.exit_code == 0

    validate_snapshot_request.assert_not_called()
    run_snapshot.assert_not_called()


def test_snapshot_validation_failure(
    mocker: MockerFixture, snapshot_request: SnapshotRequest
):

    error = GyomuError(
        message="validation failed",
        domain="test",
        operation="validate",
        reason="invalid_input",
    )

    mocker.patch(
        "gyomu_cli.main.translate_snapshot_request",
        return_value=Success(snapshot_request),
    )
    mocker.patch(
        "gyomu_cli.main.validate_snapshot_request",
        return_value=Failure(error),
    )
    run_snapshot = mocker.patch(
        "gyomu_cli.main.run_snapshot",
    )

    result = runner.invoke(
        app,
        [
            "snapshot",
            "test-package",
        ],
    )

    assert result.exit_code == 0

    run_snapshot.assert_not_called()


def test_snapshot_run_failure(mocker: MockerFixture, snapshot_request: SnapshotRequest):

    error = GyomuError(
        message="run failed",
        domain="test",
        operation="run",
        reason="invalid_input",
    )

    mocker.patch(
        "gyomu_cli.main.translate_snapshot_request",
        return_value=Success(snapshot_request),
    )
    mocker.patch(
        "gyomu_cli.main.validate_snapshot_request",
        return_value=Success(None),
    )
    mocker.patch(
        "gyomu_cli.main.run_snapshot",
        return_value=Failure(error),
    )

    result = runner.invoke(
        app,
        [
            "snapshot",
            "test-package",
        ],
    )

    assert result.exit_code == 0
