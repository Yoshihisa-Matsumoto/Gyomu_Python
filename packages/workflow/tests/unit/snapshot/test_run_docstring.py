from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.option.update import UpdateOption
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_workflow.snapshot.run import build_docstring_update_option
from gyomu_workflow.snapshot.run_docstring import run_docstring_action
from returns.result import Failure, Success

from packages.python_analysis.python_analysis_test_support.helpers import (
    _create_context,
)


@pytest.fixture
def update_option() -> UpdateOption:
    return build_docstring_update_option(None)


@pytest.fixture
def source_project_relative_path() -> ProjectRelativePath:
    return ProjectRelativePath(Path("src/example.py"))


@pytest.fixture
def project_context() -> ProjectContext:
    return _create_context()


@pytest.mark.asyncio
async def test_load_file_analysis_context_failure(
    mocker,
    project_context,
    source_project_relative_path,
    update_option,
):
    error = GyomuError(
        message="load failed",
        domain="test",
        operation="load",
        reason="invalid_input",
    )

    mocker.patch(
        "gyomu_workflow.snapshot.run_docstring.load_file_analysis_context",
        return_value=Failure(error),
    )
    process_docstring_update = mocker.patch(
        "gyomu_workflow.snapshot.run_docstring.process_docstring_update",
        new_callable=AsyncMock,
    )

    result = await run_docstring_action(
        project_context=project_context,
        source_project_relative_path=source_project_relative_path,
        option=update_option,
    )

    assert isinstance(result, Failure)

    wrapped_error = result.failure()

    assert wrapped_error.message == "fail to analyze source file"
    assert wrapped_error.domain == "snapshot"
    assert wrapped_error.operation == "run_docstring_action"
    assert wrapped_error.reason == "external_failure"
    assert wrapped_error.details == {
        "file_path": source_project_relative_path,
    }

    process_docstring_update.assert_not_awaited()


@pytest.mark.asyncio
async def test_process_docstring_update_failure(
    mocker,
    project_context,
    source_project_relative_path,
    update_option,
):
    file_context = mocker.Mock()

    error = GyomuError(
        message="update failed",
        domain="test",
        operation="update",
        reason="invalid_input",
    )

    mocker.patch(
        "gyomu_workflow.snapshot.run_docstring.load_file_analysis_context",
        return_value=Success(file_context),
    )
    mocker.patch(
        "gyomu_workflow.snapshot.run_docstring.process_docstring_update",
        new_callable=AsyncMock,
        return_value=Failure(error),
    )

    result = await run_docstring_action(
        project_context=project_context,
        source_project_relative_path=source_project_relative_path,
        option=update_option,
    )

    assert isinstance(result, Failure)

    wrapped_error = result.failure()

    assert wrapped_error.message == "fail to update docstring"
    assert wrapped_error.domain == "snapshot"
    assert wrapped_error.operation == "run_docstring_action"
    assert wrapped_error.reason == "external_failure"
    assert wrapped_error.details == {
        "file_path": source_project_relative_path,
    }


@pytest.mark.asyncio
async def test_success(
    mocker,
    project_context,
    source_project_relative_path,
    update_option,
):
    file_context = mocker.Mock()

    load_file_analysis_context = mocker.patch(
        "gyomu_workflow.snapshot.run_docstring.load_file_analysis_context",
        return_value=Success(file_context),
    )
    process_docstring_update = mocker.patch(
        "gyomu_workflow.snapshot.run_docstring.process_docstring_update",
        new_callable=AsyncMock,
        return_value=Success(None),
    )

    result = await run_docstring_action(
        project_context=project_context,
        source_project_relative_path=source_project_relative_path,
        option=update_option,
    )

    assert isinstance(result, Success)
    assert result.unwrap() is None

    load_file_analysis_context.assert_called_once_with(
        context=project_context,
        file_path=source_project_relative_path,
        option=update_option,
    )

    process_docstring_update.assert_awaited_once_with(
        context=project_context,
        file_context=file_context,
        option=update_option,
    )
