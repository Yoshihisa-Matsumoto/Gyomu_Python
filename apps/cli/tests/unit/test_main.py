from unittest.mock import call

import pytest
from gyomu_cli.main import app
from gyomu_python_analysis.project.workspace import (
    WorkspaceProject,
)
from gyomu_schema.error.gyomu import GyomuError
from pytest_mock import MockerFixture
from returns.result import Failure, Success
from typer.testing import CliRunner

from packages.concept.concept_test_support.helpers import create_workspace_context
from packages.python_analysis.test_support.helpers import (
    create_py_project_config,
    create_workspace_project,
)

runner = CliRunner()


def create_project(
    name: str,
) -> WorkspaceProject:
    project = create_workspace_project(config=create_py_project_config(name=name))
    return project


@pytest.fixture
def setup_snapshot(mocker: MockerFixture) -> None:
    mocker.patch("gyomu_cli.main.register_google_routing")
    mocker.patch("gyomu_cli.main.get_workspace_context")
    mocker.patch("gyomu_cli.main.run_snapshot_request")


def test_snapshot_single_package_success(
    mocker: MockerFixture,
    setup_snapshot: None,
) -> None:
    project = create_project(name="gyomu-ai")
    workspace = create_workspace_context(projects=(project,))

    mocker.patch(
        "gyomu_cli.main.get_workspace_context",
        return_value=Success(workspace),
    )
    mocker.patch(
        "gyomu_cli.main.find_project_by_name",
        return_value=Success(project),
    )
    run_mock = mocker.patch(
        "gyomu_cli.main.run_snapshot_request",
        return_value=Success(None),
    )
    logger_mock = mocker.patch("gyomu_cli.main.logger.info")

    result = runner.invoke(app, ["snapshot", "--package", "gyomu-ai"])

    assert result.exit_code == 0, result.output
    run_mock.assert_called_once()
    args = run_mock.call_args.args
    assert args[0] is workspace
    assert args[1] is project
    assert args[2].commit is True
    assert args[2].action.docstring.enabled is True
    assert args[2].target.all is False

    logger_mock.assert_any_call("Done")


def test_snapshot_workspace_failure(
    mocker: MockerFixture,
    setup_snapshot: None,
) -> None:
    error = GyomuError(
        message="workspace not found",
        domain="test",
        operation="workspace",
        reason="invalid_input",
    )
    mocker.patch(
        "gyomu_cli.main.get_workspace_context",
        return_value=Failure(error),
    )
    logger_mock = mocker.patch("gyomu_cli.main.logger.error_object")
    run_mock = mocker.patch("gyomu_cli.main.run_snapshot_request")

    result = runner.invoke(app, ["snapshot"])

    assert result.exit_code == 0
    logger_mock.assert_called_once_with(error)
    run_mock.assert_not_called()


def test_snapshot_package_not_found(
    mocker: MockerFixture,
    setup_snapshot: None,
) -> None:
    workspace = create_workspace_context(projects=())
    error = GyomuError(
        message="project not found",
        domain="test",
        operation="package search",
        reason="invalid_input",
    )
    mocker.patch(
        "gyomu_cli.main.get_workspace_context",
        return_value=Success(workspace),
    )
    mocker.patch(
        "gyomu_cli.main.find_project_by_name",
        return_value=Failure(error),
    )
    error_logger = mocker.patch("gyomu_cli.main.logger.error")
    error_object_logger = mocker.patch("gyomu_cli.main.logger.error_object")
    run_mock = mocker.patch("gyomu_cli.main.run_snapshot_request")

    result = runner.invoke(app, ["snapshot", "--package", "unknown-package"])

    assert result.exit_code == 0
    error_logger.assert_called_once_with("unknown-package Not Found")
    error_object_logger.assert_called_once_with(error)
    run_mock.assert_not_called()


def test_snapshot_all_projects_success(
    mocker: MockerFixture,
    setup_snapshot: None,
) -> None:
    first_project = create_project("gyomu-schema")
    second_project = create_project("gyomu-ai")
    workspace = create_workspace_context(
        projects=(first_project, second_project),
    )

    mocker.patch(
        "gyomu_cli.main.get_workspace_context",
        return_value=Success(workspace),
    )
    find_mock = mocker.patch("gyomu_cli.main.find_project_by_name")
    run_mock = mocker.patch(
        "gyomu_cli.main.run_snapshot_request",
        return_value=Success(None),
    )
    logger_mock = mocker.patch("gyomu_cli.main.logger.info")

    result = runner.invoke(app, ["snapshot"])

    assert result.exit_code == 0
    find_mock.assert_not_called()
    assert run_mock.call_count == 2
    assert run_mock.call_args_list[0].args[:2] == (
        workspace,
        first_project,
    )
    assert run_mock.call_args_list[1].args[:2] == (
        workspace,
        second_project,
    )
    logger_mock.assert_any_call("Processing package: gyomu-schema")
    logger_mock.assert_any_call("Processing package: gyomu-ai")
    logger_mock.assert_any_call("Done")


def test_snapshot_all_projects_stops_on_failure(
    mocker: MockerFixture,
    setup_snapshot: None,
) -> None:
    first_project = create_project("gyomu-schema")
    second_project = create_project("gyomu-ai")
    third_project = create_project("gyomu-workflow")
    workspace = create_workspace_context(
        projects=(first_project, second_project, third_project),
    )
    error = GyomuError(
        message="snapshot failed",
        domain="test",
        operation="snapshot",
        reason="invalid_input",
    )

    mocker.patch(
        "gyomu_cli.main.get_workspace_context",
        return_value=Success(workspace),
    )
    run_mock = mocker.patch(
        "gyomu_cli.main.run_snapshot_request",
        side_effect=[
            Success(None),
            Failure(error),
        ],
    )
    logger_mock = mocker.patch("gyomu_cli.main.logger.info")

    result = runner.invoke(app, ["snapshot"])

    assert result.exit_code == 0
    assert run_mock.call_count == 2
    assert run_mock.call_args_list[0].args[1] is first_project
    assert run_mock.call_args_list[1].args[1] is second_project
    assert call("Processing package: gyomu-workflow") not in (
        logger_mock.call_args_list
    )
    assert call("Done") not in logger_mock.call_args_list
