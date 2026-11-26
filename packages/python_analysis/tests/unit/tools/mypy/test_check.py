import logging
from dataclasses import replace
from pathlib import Path
from unittest.mock import call

import pytest
from gyomu_infra.process.model import ProcessResult
from gyomu_python_analysis.analysis.workspace import find_root
from gyomu_python_analysis.error.tools import MypyCheckExecutionError
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_python_analysis.tools.mypy.check import (
    _execute_mypy,
    check_file,
    check_project,
    check_project_target,
    check_workspace,
    check_workspace_target,
)
from gyomu_python_analysis.tools.mypy.models import (
    MypyCheckConfig,
    MypyCheckReport,
    MypyCheckResult,
    MypyCheckResults,
    MypyTarget,
)
from gyomu_schema.schemas.python.types import WorkspaceRelativePath
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.infra.test_support.helpers import create_process_error
from packages.python_analysis.test_support.helpers import (
    MONOREPO_FIXTURES_ROOT,
    create_mypy_check_config,
    create_mypy_check_execution_error,
    create_mypy_check_result,
)


@pytest.fixture
def workspace_context() -> WorkspaceContext:
    result = find_root(MONOREPO_FIXTURES_ROOT)
    assert isinstance(result, Success)
    return result.unwrap()


@pytest.fixture
def target_project_context(workspace_context: WorkspaceContext) -> ProjectContext:
    target_project_context = workspace_context.get_project_context("project-a")
    assert target_project_context is not None
    return target_project_context


class Test_ExecuteMypy:
    def test_success(
        self,
        mocker: MockerFixture,
    ) -> None:
        mypy_check_config = create_mypy_check_config()
        execute_mock = mocker.patch(
            "gyomu_python_analysis.tools.mypy.check.execute",
            return_value=Success(
                ProcessResult(
                    exit_code=0,
                    stdout="Success: no issues found in 1 source file\n",
                    stderr="",
                )
            ),
        )

        actual = _execute_mypy(config=mypy_check_config)

        assert isinstance(actual, Success)
        assert actual.unwrap().diagnostics == ()
        execute_mock.assert_called_once()

    def test_diagnostics(
        self,
        mocker: MockerFixture,
    ) -> None:
        mypy_check_config = create_mypy_check_config()
        stdout = (
            "example.py:1: error: Incompatible types [assignment]\n"
            "Found 1 error in 1 file\n"
        )
        mocker.patch(
            "gyomu_python_analysis.tools.mypy.check.execute",
            return_value=Success(
                ProcessResult(
                    exit_code=1,
                    stdout=stdout,
                    stderr="",
                )
            ),
        )

        actual = _execute_mypy(config=mypy_check_config)

        assert isinstance(actual, Success)
        assert actual.unwrap().diagnostics == tuple(stdout.splitlines())

    def test_exit_code_1_without_stdout(
        self,
        mocker: MockerFixture,
    ) -> None:
        mypy_check_config = create_mypy_check_config()
        mocker.patch(
            "gyomu_python_analysis.tools.mypy.check.execute",
            return_value=Success(
                ProcessResult(exit_code=1, stdout="", stderr="unexpected")
            ),
        )

        actual = _execute_mypy(config=mypy_check_config)

        assert isinstance(actual, Failure)
        assert isinstance(actual.failure(), MypyCheckExecutionError)

    def test_unexpected_exit_code(
        self,
        mocker: MockerFixture,
    ) -> None:
        mypy_check_config = create_mypy_check_config()
        mocker.patch(
            "gyomu_python_analysis.tools.mypy.check.execute",
            return_value=Success(
                ProcessResult(exit_code=2, stdout="", stderr="fatal error")
            ),
        )

        actual = _execute_mypy(config=mypy_check_config)

        assert isinstance(actual, Failure)
        assert isinstance(actual.failure(), MypyCheckExecutionError)

    def test_execute_failure(
        self,
        mocker: MockerFixture,
    ) -> None:
        mypy_check_config = create_mypy_check_config()
        process_error = create_process_error(message="process failed")

        mocker.patch(
            "gyomu_python_analysis.tools.mypy.check.execute",
            return_value=Failure(process_error),
        )

        actual = _execute_mypy(config=mypy_check_config)

        assert isinstance(actual, Failure)

        error = actual.failure()
        assert isinstance(error, MypyCheckExecutionError)
        assert error.__cause__ is process_error

    def test_skips_when_targets_are_empty(
        self,
        mocker: MockerFixture,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        config = replace(
            create_mypy_check_config(),
            targets=(),
        )
        mock_execute = mocker.patch(
            "gyomu_python_analysis.tools.mypy.check.execute",
        )

        with caplog.at_level(
            logging.WARNING,
            logger="gyomu_python_analysis.tools.mypy.check",
        ):
            result = _execute_mypy(config=config)

        assert isinstance(result, Success)
        assert result.unwrap().diagnostics == ()
        assert result.unwrap().skipped_reason == "No targets configured"
        assert "No targets configured. skip mypy" in caplog.text
        mock_execute.assert_not_called()


class TestCheckProjectTarget:
    def test_returns_execute_result(
        self,
        workspace_context: WorkspaceContext,
        mocker: MockerFixture,
    ) -> None:
        target_project_context = workspace_context.get_project_context("project-b")
        assert target_project_context is not None

        target = MypyTarget.SOURCE
        config = MypyCheckConfig(
            targets=(target_project_context.project_root / "src",),
            config_file=Path("pyproject.toml"),
            cache_dir=None,
            explicit_package_bases=False,
            working_directory=workspace_context.root_project_context.project_root,
            mypy_path=None,
        )
        check_result = MypyCheckResult(
            name=str(target),
            diagnostics=(),
        )

        for_project_mock = mocker.patch(
            "gyomu_python_analysis.tools.mypy.check.for_project",
            return_value=config,
        )
        execute_mock = mocker.patch(
            "gyomu_python_analysis.tools.mypy.check._execute_mypy",
            return_value=Success(check_result),
        )

        actual = check_project_target(
            target=target,
            target_project_context=target_project_context,
            workspace_context=workspace_context,
        )

        assert actual == Success(check_result)
        for_project_mock.assert_called_once_with(
            target=target,
            target_project_context=target_project_context,
            workspace_context=workspace_context,
        )
        execute_mock.assert_called_once_with(config=config)

    def test_returns_execute_failure(
        self,
        workspace_context: WorkspaceContext,
        mocker: MockerFixture,
    ) -> None:
        target_project_context = workspace_context.get_project_context("project-b")
        assert target_project_context is not None

        config = MypyCheckConfig(
            targets=(target_project_context.project_root / "src",),
            config_file=Path("pyproject.toml"),
            cache_dir=None,
            explicit_package_bases=False,
            working_directory=workspace_context.root_project_context.project_root,
            mypy_path=None,
        )
        error = create_mypy_check_execution_error(message="mypy failed")

        mocker.patch(
            "gyomu_python_analysis.tools.mypy.check.for_project",
            return_value=config,
        )
        execute_mock = mocker.patch(
            "gyomu_python_analysis.tools.mypy.check._execute_mypy",
            return_value=Failure(error),
        )

        actual = check_project_target(
            target=MypyTarget.SOURCE,
            target_project_context=target_project_context,
            workspace_context=workspace_context,
        )

        assert actual == Failure(error)
        execute_mock.assert_called_once_with(config=config)


class TestCheckFile:
    def test_returns_execute_result(
        self,
        mocker: MockerFixture,
        target_project_context: ProjectContext,
        workspace_context: WorkspaceContext,
    ) -> None:
        workspace_relative_file_path = WorkspaceRelativePath(
            Path("packages/project-a/src/example.py")
        )
        config = create_mypy_check_config()
        expected_result = Success(create_mypy_check_result(name="example.py"))

        mock_for_file = mocker.patch(
            "gyomu_python_analysis.tools.mypy.check.for_file",
            return_value=config,
        )
        mock_execute_mypy = mocker.patch(
            "gyomu_python_analysis.tools.mypy.check._execute_mypy",
            return_value=expected_result,
        )

        result = check_file(
            workspace_relative_file_path=workspace_relative_file_path,
            target_project_context=target_project_context,
            workspace_context=workspace_context,
        )

        assert result is expected_result
        mock_for_file.assert_called_once_with(
            workspace_relative_file_path=workspace_relative_file_path,
            target_project_context=target_project_context,
            workspace_context=workspace_context,
        )
        mock_execute_mypy.assert_called_once_with(config=config)

    def test_returns_execute_failure(
        self,
        mocker: MockerFixture,
        target_project_context: ProjectContext,
        workspace_context: WorkspaceContext,
    ) -> None:
        workspace_relative_file_path = WorkspaceRelativePath(
            Path("packages/project-a/src/example.py")
        )
        config = create_mypy_check_config()
        error = create_mypy_check_execution_error(
            message="mypy execution failed",
        )
        expected_result = Failure(error)

        mocker.patch(
            "gyomu_python_analysis.tools.mypy.check.for_file",
            return_value=config,
        )
        mock_execute_mypy = mocker.patch(
            "gyomu_python_analysis.tools.mypy.check._execute_mypy",
            return_value=expected_result,
        )

        result = check_file(
            workspace_relative_file_path=workspace_relative_file_path,
            target_project_context=target_project_context,
            workspace_context=workspace_context,
        )

        assert result is expected_result
        assert isinstance(result, Failure)
        assert result.failure() is error
        mock_execute_mypy.assert_called_once_with(config=config)


class TestCheckProject:
    def test_returns_report_with_all_results(
        self,
        workspace_context: WorkspaceContext,
        mocker: MockerFixture,
    ) -> None:
        target_project_context = workspace_context.get_project_context("project-b")
        assert target_project_context is not None

        source_result = MypyCheckResult(
            name="src",
            diagnostics=(),
        )
        test_support_result = MypyCheckResult(
            name="test_support",
            diagnostics=("test_support/helpers.py:10: error: example",),
        )
        tests_result = MypyCheckResult(
            name="tests",
            diagnostics=(),
        )

        check_target_mock = mocker.patch(
            "gyomu_python_analysis.tools.mypy.check.check_project_target",
            side_effect=[
                Success(source_result),
                Success(test_support_result),
                Success(tests_result),
            ],
        )

        actual = check_project(
            target_project_context=target_project_context,
            workspace_context=workspace_context,
        )

        expected = Success(
            MypyCheckReport(
                results=MypyCheckResults(
                    src=source_result,
                    test_support=test_support_result,
                    tests=tests_result,
                )
            )
        )

        assert actual == expected
        assert check_target_mock.call_args_list == [
            call(
                target=MypyTarget.SOURCE,
                target_project_context=target_project_context,
                workspace_context=workspace_context,
            ),
            call(
                target=MypyTarget.TEST_SUPPORT,
                target_project_context=target_project_context,
                workspace_context=workspace_context,
            ),
            call(
                target=MypyTarget.TESTS,
                target_project_context=target_project_context,
                workspace_context=workspace_context,
            ),
        ]

    def test_returns_source_failure_without_checking_remaining_targets(
        self,
        workspace_context: WorkspaceContext,
        mocker: MockerFixture,
    ) -> None:
        target_project_context = workspace_context.get_project_context("project-b")
        assert target_project_context is not None

        error = create_mypy_check_execution_error(message="source check failed")
        check_target_mock = mocker.patch(
            "gyomu_python_analysis.tools.mypy.check.check_project_target",
            return_value=Failure(error),
        )

        actual = check_project(
            target_project_context=target_project_context,
            workspace_context=workspace_context,
        )

        assert actual == Failure(error)
        check_target_mock.assert_called_once_with(
            target=MypyTarget.SOURCE,
            target_project_context=target_project_context,
            workspace_context=workspace_context,
        )

    def test_returns_test_support_failure(
        self,
        mocker: MockerFixture,
        workspace_context: WorkspaceContext,
    ) -> None:
        target_project_context = workspace_context.get_project_context("project-a")
        assert target_project_context is not None
        source_result = create_mypy_check_result(name="src")
        error = create_mypy_check_execution_error(
            message="test_support check failed",
        )

        mock_check_project_target = mocker.patch(
            "gyomu_python_analysis.tools.mypy.check.check_project_target",
            side_effect=[
                Success(source_result),
                Failure(error),
            ],
        )

        result = check_project(
            target_project_context=target_project_context,
            workspace_context=workspace_context,
        )

        assert isinstance(result, Failure)
        assert result.failure() is error
        assert mock_check_project_target.call_count == 2
        assert [
            call.kwargs["target"] for call in mock_check_project_target.call_args_list
        ] == [
            MypyTarget.SOURCE,
            MypyTarget.TEST_SUPPORT,
        ]

    def test_returns_tests_failure(
        self,
        mocker: MockerFixture,
        workspace_context: WorkspaceContext,
    ) -> None:
        target_project_context = workspace_context.get_project_context("project-a")
        assert target_project_context is not None
        source_result = create_mypy_check_result(name="src")
        test_support_result = create_mypy_check_result(name="test_support")
        error = create_mypy_check_execution_error(
            message="tests check failed",
        )

        mock_check_project_target = mocker.patch(
            "gyomu_python_analysis.tools.mypy.check.check_project_target",
            side_effect=[
                Success(source_result),
                Success(test_support_result),
                Failure(error),
            ],
        )

        result = check_project(
            target_project_context=target_project_context,
            workspace_context=workspace_context,
        )

        assert isinstance(result, Failure)
        assert result.failure() is error
        assert mock_check_project_target.call_count == 3
        assert [
            call.kwargs["target"] for call in mock_check_project_target.call_args_list
        ] == [
            MypyTarget.SOURCE,
            MypyTarget.TEST_SUPPORT,
            MypyTarget.TESTS,
        ]


class TestCheckWorkspaceTarget:
    def test_returns_execute_result(
        self,
        mocker: MockerFixture,
        workspace_context: WorkspaceContext,
    ) -> None:
        config = create_mypy_check_config()
        expected_result = Success(create_mypy_check_result(name="src"))

        mock_for_workspace = mocker.patch(
            "gyomu_python_analysis.tools.mypy.check.for_workspace",
            return_value=config,
        )
        mock_execute_mypy = mocker.patch(
            "gyomu_python_analysis.tools.mypy.check._execute_mypy",
            return_value=expected_result,
        )

        result = check_workspace_target(
            target=MypyTarget.SOURCE,
            workspace_context=workspace_context,
        )

        assert result is expected_result
        mock_for_workspace.assert_called_once_with(
            target=MypyTarget.SOURCE,
            workspace_context=workspace_context,
        )
        mock_execute_mypy.assert_called_once_with(config=config)

    def test_returns_execute_failure(
        self,
        mocker: MockerFixture,
        workspace_context: WorkspaceContext,
    ) -> None:
        config = create_mypy_check_config()
        error = create_mypy_check_execution_error(
            message="mypy execution failed",
        )
        expected_result = Failure(error)

        mocker.patch(
            "gyomu_python_analysis.tools.mypy.check.for_workspace",
            return_value=config,
        )
        mock_execute_mypy = mocker.patch(
            "gyomu_python_analysis.tools.mypy.check._execute_mypy",
            return_value=expected_result,
        )

        result = check_workspace_target(
            target=MypyTarget.SOURCE,
            workspace_context=workspace_context,
        )

        assert result is expected_result
        assert isinstance(result, Failure)
        assert result.failure() is error
        mock_execute_mypy.assert_called_once_with(config=config)


class TestCheckWorkspace:
    def test_returns_report_with_all_results(
        self,
        mocker: MockerFixture,
        workspace_context: WorkspaceContext,
    ) -> None:
        source_result = create_mypy_check_result(name="src")
        test_support_result = create_mypy_check_result(name="test_support")
        tests_result = create_mypy_check_result(name="tests")

        mock_check_workspace_target = mocker.patch(
            "gyomu_python_analysis.tools.mypy.check.check_workspace_target",
            side_effect=[
                Success(source_result),
                Success(test_support_result),
                Success(tests_result),
            ],
        )

        result = check_workspace(workspace_context=workspace_context)

        assert isinstance(result, Success)
        report = result.unwrap()
        assert report.results.src is source_result
        assert report.results.test_support is test_support_result
        assert report.results.tests is tests_result

        assert [
            call.kwargs["target"] for call in mock_check_workspace_target.call_args_list
        ] == [
            MypyTarget.SOURCE,
            MypyTarget.TEST_SUPPORT,
            MypyTarget.TESTS,
        ]
        assert all(
            call.kwargs["workspace_context"] is workspace_context
            for call in mock_check_workspace_target.call_args_list
        )

    def test_returns_source_failure(
        self,
        mocker: MockerFixture,
        workspace_context: WorkspaceContext,
    ) -> None:
        error = create_mypy_check_execution_error(
            message="source check failed",
        )

        mock_check_workspace_target = mocker.patch(
            "gyomu_python_analysis.tools.mypy.check.check_workspace_target",
            return_value=Failure(error),
        )

        result = check_workspace(workspace_context=workspace_context)

        assert isinstance(result, Failure)
        assert result.failure() is error
        assert mock_check_workspace_target.call_count == 1
        mock_check_workspace_target.assert_called_once_with(
            target=MypyTarget.SOURCE,
            workspace_context=workspace_context,
        )

    def test_returns_test_support_failure(
        self,
        mocker: MockerFixture,
        workspace_context: WorkspaceContext,
    ) -> None:
        source_result = create_mypy_check_result(name="src")
        error = create_mypy_check_execution_error(
            message="test_support check failed",
        )

        mock_check_workspace_target = mocker.patch(
            "gyomu_python_analysis.tools.mypy.check.check_workspace_target",
            side_effect=[
                Success(source_result),
                Failure(error),
            ],
        )

        result = check_workspace(workspace_context=workspace_context)

        assert isinstance(result, Failure)
        assert result.failure() is error
        assert [
            call.kwargs["target"] for call in mock_check_workspace_target.call_args_list
        ] == [
            MypyTarget.SOURCE,
            MypyTarget.TEST_SUPPORT,
        ]

    def test_returns_tests_failure(
        self,
        mocker: MockerFixture,
        workspace_context: WorkspaceContext,
    ) -> None:
        source_result = create_mypy_check_result(name="src")
        test_support_result = create_mypy_check_result(name="test_support")
        error = create_mypy_check_execution_error(
            message="tests check failed",
        )

        mock_check_workspace_target = mocker.patch(
            "gyomu_python_analysis.tools.mypy.check.check_workspace_target",
            side_effect=[
                Success(source_result),
                Success(test_support_result),
                Failure(error),
            ],
        )

        result = check_workspace(workspace_context=workspace_context)

        assert isinstance(result, Failure)
        assert result.failure() is error
        assert [
            call.kwargs["target"] for call in mock_check_workspace_target.call_args_list
        ] == [
            MypyTarget.SOURCE,
            MypyTarget.TEST_SUPPORT,
            MypyTarget.TESTS,
        ]
