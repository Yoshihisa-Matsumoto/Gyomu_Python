from pathlib import Path
from unittest.mock import MagicMock

from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_schema.schemas.types import FullPath
from gyomu_workflow.snapshot.workspace import get_workspace_context
from pytest_mock import MockerFixture
from returns.result import Failure, Success


def test_returns_workspace_context(
    mocker: MockerFixture,
) -> None:
    current_path = FullPath(Path("/workspace/project"))
    workspace = MagicMock()
    workspace_context = MagicMock(spec=WorkspaceContext)

    mocker.patch(
        "gyomu_workflow.snapshot.workspace.find_root",
        return_value=Success(workspace),
    )
    initialize_mock = mocker.patch(
        "gyomu_workflow.snapshot.workspace.initialize_workspace_context",
        return_value=Success(workspace_context),
    )

    result = get_workspace_context(current_path)

    assert isinstance(result, Success)
    assert result.unwrap() is workspace_context
    initialize_mock.assert_called_once_with(workspace)


def test_returns_failure_when_root_not_found(
    mocker: MockerFixture,
) -> None:
    current_path = FullPath(Path("/workspace/project"))
    error = MagicMock(spec=AnalysisError)

    mocker.patch(
        "gyomu_workflow.snapshot.workspace.find_root",
        return_value=Failure(error),
    )
    initialize_mock = mocker.patch(
        "gyomu_workflow.snapshot.workspace.initialize_workspace_context",
    )
    logger_mock = mocker.patch(
        "gyomu_workflow.snapshot.workspace.logger.error_object",
    )

    result = get_workspace_context(current_path)

    assert isinstance(result, Failure)
    assert result.failure() is error
    logger_mock.assert_called_once_with(error)
    initialize_mock.assert_not_called()


def test_returns_failure_when_workspace_initialization_fails(
    mocker: MockerFixture,
) -> None:
    current_path = FullPath(Path("/workspace/project"))
    workspace = MagicMock()
    error = MagicMock(spec=AnalysisError)

    mocker.patch(
        "gyomu_workflow.snapshot.workspace.find_root",
        return_value=Success(workspace),
    )
    mocker.patch(
        "gyomu_workflow.snapshot.workspace.initialize_workspace_context",
        return_value=Failure(error),
    )

    result = get_workspace_context(current_path)

    assert isinstance(result, Failure)
    assert result.failure() is error
