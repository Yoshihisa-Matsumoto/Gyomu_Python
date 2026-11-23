import sys
from pathlib import Path

import pytest
from gyomu_infra.process.model import ProcessResult
from gyomu_python_analysis.analysis.initialize import initialize_project_context
from gyomu_python_analysis.analysis.workspace import find_root
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_python_analysis.tools.ruff.check import (
    _check_format,
    _check_lint,
    _format,
    check_file_format,
    check_file_lint,
    check_project_format,
    check_project_lint,
    check_workspace_format,
    check_workspace_lint,
    format_file,
)
from gyomu_python_analysis.tools.ruff.config import for_project
from gyomu_python_analysis.tools.ruff.models import RuffCheckConfig, RuffCheckResult
from gyomu_schema.schemas.python.types import ProjectRelativePath
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.python_analysis.test_support.helpers import MONOREPO_FIXTURES_ROOT


@pytest.fixture
def workspace_context() -> WorkspaceContext:
    result = find_root(MONOREPO_FIXTURES_ROOT)
    assert isinstance(result, Success)
    return result.unwrap()


@pytest.fixture
def root_project_context(workspace_context: WorkspaceContext) -> ProjectContext:
    root_context_result = initialize_project_context(
        project_root=workspace_context.workspace_root.path,
        source_root=ProjectRelativePath(Path(".")),
    )
    assert isinstance(root_context_result, Success)
    return root_context_result.unwrap()


class TestCheckFormat:
    def test_success(
        self,
        mocker,
    ) -> None:
        config = RuffCheckConfig(
            target=Path("/workspace/example.py"),
            working_directory=Path("/workspace"),
        )
        mock_execute = mocker.patch(
            "gyomu_python_analysis.tools.ruff.check.execute",
            return_value=Success(
                ProcessResult(
                    exit_code=0,
                    stdout="1 file already formatted\n",
                    stderr="",
                )
            ),
        )

        actual = _check_format(config)

        assert isinstance(actual, Success)
        mock_execute.assert_called_once_with(
            command=[
                sys.executable,
                "-m",
                "ruff",
                "format",
                "--check",
                "/workspace/example.py",
            ],
            cwd=Path("/workspace"),
        )

    def test_returns_diagnostics_when_format_is_needed(
        self,
        mocker,
    ) -> None:
        config = RuffCheckConfig(
            target=Path("/workspace/example.py"),
            working_directory=Path("/workspace"),
        )
        mocker.patch(
            "gyomu_python_analysis.tools.ruff.check.execute",
            return_value=Success(
                ProcessResult(
                    exit_code=1,
                    stdout="Would reformat: /workspace/example.py\n",
                    stderr="",
                )
            ),
        )

        actual = _check_format(config)

        assert isinstance(actual, Success)
        assert actual.unwrap().diagnostics == ("Would reformat: /workspace/example.py",)
        assert not actual.unwrap().success

    def test_returns_failure_when_execution_returns_unexpected(
        self,
        mocker,
    ) -> None:
        config = RuffCheckConfig(
            target=Path("/workspace/example.py"),
            working_directory=Path("/workspace"),
        )
        mocker.patch(
            "gyomu_python_analysis.tools.ruff.check.execute",
            return_value=Success(
                ProcessResult(
                    exit_code=2,
                    stdout="stdout",
                    stderr="stderr",
                )
            ),
        )

        actual = _check_format(config)

        assert isinstance(actual, Failure)
        failure = actual.failure()
        assert failure.details
        assert failure.details["stdout"] == "stdout"
        assert failure.details["stderr"] == "stderr"
        assert failure.command == [
            sys.executable,
            "-m",
            "ruff",
            "format",
            "--check",
            "/workspace/example.py",
        ]

    def test_returns_failure_when_execution_fails(
        self,
        mocker,
    ) -> None:
        config = RuffCheckConfig(
            target=Path("/workspace/example.py"),
            working_directory=Path("/workspace"),
        )
        execution_error = RuntimeError("process execution failed")
        mocker.patch(
            "gyomu_python_analysis.tools.ruff.check.execute",
            return_value=Failure(execution_error),
        )

        actual = _check_format(config)

        assert isinstance(actual, Failure)
        assert actual.failure() is not execution_error


class TestCheckLint:
    def test_success(
        self,
        mocker,
    ) -> None:
        config = RuffCheckConfig(
            target=Path("/workspace/example.py"),
            working_directory=Path("/workspace"),
        )
        mock_execute = mocker.patch(
            "gyomu_python_analysis.tools.ruff.check.execute",
            return_value=Success(
                ProcessResult(
                    exit_code=0,
                    stdout="All checks passed!\n",
                    stderr="",
                )
            ),
        )

        actual = _check_lint(config)

        assert isinstance(actual, Success)
        assert actual.unwrap().success
        assert actual.unwrap().diagnostics == ()
        mock_execute.assert_called_once_with(
            command=[
                sys.executable,
                "-m",
                "ruff",
                "check",
                "/workspace/example.py",
            ],
            cwd=Path("/workspace"),
        )

    def test_returns_diagnostics_when_violations_exist(
        self,
        mocker,
    ) -> None:
        config = RuffCheckConfig(
            target=Path("/workspace/example.py"),
            working_directory=Path("/workspace"),
        )
        mocker.patch(
            "gyomu_python_analysis.tools.ruff.check.execute",
            return_value=Success(
                ProcessResult(
                    exit_code=1,
                    stdout=(
                        "example.py:1:1: F401 `os` imported but unused\n"
                        "Found 1 error.\n"
                    ),
                    stderr="",
                )
            ),
        )

        actual = _check_lint(config)

        assert isinstance(actual, Success)
        assert actual.unwrap().diagnostics == (
            "example.py:1:1: F401 `os` imported but unused",
            "Found 1 error.",
        )
        assert not actual.unwrap().success


class TestFormat:
    def test_success(
        self,
        mocker,
    ) -> None:
        config = RuffCheckConfig(
            target=Path("/workspace/example.py"),
            working_directory=Path("/workspace"),
        )
        mock_execute = mocker.patch(
            "gyomu_python_analysis.tools.ruff.check.execute",
            side_effect=[
                Success(
                    ProcessResult(
                        exit_code=0,
                        stdout="1 file reformatted\n",
                        stderr="",
                    )
                ),
                Success(
                    ProcessResult(
                        exit_code=0,
                        stdout="Found 3 errors (3 fixed, 0 remaining).\n",
                        stderr="",
                    )
                ),
            ],
        )

        actual = _format(config)

        assert isinstance(actual, Success)

        assert mock_execute.call_count == 2
        assert mock_execute.call_args_list == [
            mocker.call(
                command=[
                    sys.executable,
                    "-m",
                    "ruff",
                    "format",
                    "/workspace/example.py",
                ],
                cwd=Path("/workspace"),
            ),
            mocker.call(
                command=[
                    sys.executable,
                    "-m",
                    "ruff",
                    "check",
                    "--select",
                    "I",
                    "--fix",
                    "/workspace/example.py",
                ],
                cwd=Path("/workspace"),
            ),
        ]


class TestCheckProjectFormat:
    def test_delegates_to_check_format(
        self,
        workspace_context: WorkspaceContext,
        root_project_context: ProjectContext,
        mocker: MockerFixture,
    ) -> None:
        target_project_context = workspace_context.get_project_context("project-b")
        assert target_project_context is not None

        expected = Success(
            RuffCheckResult(
                name=str(target_project_context.project_root),
                diagnostics=(),
            )
        )
        mock_check_format = mocker.patch(
            "gyomu_python_analysis.tools.ruff.check._check_format",
            return_value=expected,
        )

        actual = check_project_format(
            target_project_context=target_project_context,
            workspace_root_project_context=root_project_context,
            workspace_context=workspace_context,
        )

        assert actual == expected
        mock_check_format.assert_called_once_with(
            config=for_project(
                target_project_context=target_project_context,
                workspace_root_project_context=root_project_context,
                workspace_context=workspace_context,
            )
        )


class TestCheckFileFormat:
    def test_delegates_to_check_format(
        self,
        workspace_context: WorkspaceContext,
        root_project_context: ProjectContext,
        mocker: MockerFixture,
    ) -> None:
        target_project_context = workspace_context.get_project_context("project-b")
        assert target_project_context is not None

        workspace_relative_file_path = ProjectRelativePath(
            Path("packages/project-a/src/example.py")
        )
        expected = Success(
            RuffCheckResult(
                name="example.py",
                diagnostics=(),
            )
        )
        mock_check_format = mocker.patch(
            "gyomu_python_analysis.tools.ruff.check._check_format",
            return_value=expected,
        )
        mock_for_file = mocker.patch(
            "gyomu_python_analysis.tools.ruff.check.for_file",
            return_value=RuffCheckConfig(
                target=Path("/workspace/example.py"),
                working_directory=Path("/workspace"),
            ),
        )

        actual = check_file_format(
            workspace_relative_file_path=workspace_relative_file_path,
            target_project_context=target_project_context,
            workspace_root_project_context=root_project_context,
            workspace_context=workspace_context,
        )

        assert actual == expected
        mock_for_file.assert_called_once_with(
            workspace_relative_file_path=workspace_relative_file_path,
            target_project_context=target_project_context,
            workspace_root_project_context=root_project_context,
            workspace_context=workspace_context,
        )
        mock_check_format.assert_called_once_with(
            config=RuffCheckConfig(
                target=Path("/workspace/example.py"),
                working_directory=Path("/workspace"),
            )
        )


class TestFormatFile:
    def test_delegates_to_format(
        self,
        workspace_context: WorkspaceContext,
        root_project_context: ProjectContext,
        mocker: MockerFixture,
    ) -> None:
        target_project_context = workspace_context.get_project_context("project-b")
        assert target_project_context is not None

        workspace_relative_file_path = ProjectRelativePath(
            Path("packages/project-a/src/example.py")
        )
        config = RuffCheckConfig(
            target=Path("/workspace/example.py"),
            working_directory=Path("/workspace"),
        )
        expected = Success(
            RuffCheckResult(
                name=str(config.target),
                diagnostics=(),
            )
        )
        mock_for_file = mocker.patch(
            "gyomu_python_analysis.tools.ruff.check.for_file",
            return_value=config,
        )
        mock_format = mocker.patch(
            "gyomu_python_analysis.tools.ruff.check._format",
            return_value=expected,
        )

        actual = format_file(
            workspace_relative_file_path=workspace_relative_file_path,
            target_project_context=target_project_context,
            workspace_root_project_context=root_project_context,
            workspace_context=workspace_context,
        )

        assert actual == expected
        mock_for_file.assert_called_once_with(
            workspace_relative_file_path=workspace_relative_file_path,
            target_project_context=target_project_context,
            workspace_root_project_context=root_project_context,
            workspace_context=workspace_context,
        )
        mock_format.assert_called_once_with(config=config)


class TestCheckWorkspaceFormat:
    def test_delegates_to_check_format(
        self,
        workspace_context: WorkspaceContext,
        mocker: MockerFixture,
    ) -> None:
        config = RuffCheckConfig(
            target=workspace_context.workspace_root.path,
            working_directory=workspace_context.workspace_root.path,
        )
        expected = Success(
            RuffCheckResult(
                name=str(config.target),
                diagnostics=(),
            )
        )
        mock_for_workspace = mocker.patch(
            "gyomu_python_analysis.tools.ruff.check.for_workspace",
            return_value=config,
        )
        mock_check_format = mocker.patch(
            "gyomu_python_analysis.tools.ruff.check._check_format",
            return_value=expected,
        )

        actual = check_workspace_format(
            workspace_context=workspace_context,
        )

        assert actual == expected
        mock_for_workspace.assert_called_once_with(
            workspace_context=workspace_context,
        )
        mock_check_format.assert_called_once_with(config=config)


class TestCheckFileLint:
    def test_delegates_to_check_lint(
        self,
        workspace_context: WorkspaceContext,
        root_project_context: ProjectContext,
        mocker: MockerFixture,
    ) -> None:
        target_project_context = workspace_context.get_project_context("project-b")
        assert target_project_context is not None

        workspace_relative_file_path = ProjectRelativePath(
            Path("packages/project-a/src/example.py")
        )
        config = RuffCheckConfig(
            target=root_project_context.project_root / workspace_relative_file_path,
            working_directory=root_project_context.project_root,
        )
        expected = Success(RuffCheckResult(name=str(config.target), diagnostics=()))

        mock_for_file = mocker.patch(
            "gyomu_python_analysis.tools.ruff.check.for_file",
            return_value=config,
        )
        mock_check_lint = mocker.patch(
            "gyomu_python_analysis.tools.ruff.check._check_lint",
            return_value=expected,
        )

        actual = check_file_lint(
            workspace_relative_file_path=workspace_relative_file_path,
            target_project_context=target_project_context,
            workspace_root_project_context=root_project_context,
            workspace_context=workspace_context,
        )

        assert actual == expected
        mock_for_file.assert_called_once_with(
            workspace_relative_file_path=workspace_relative_file_path,
            target_project_context=target_project_context,
            workspace_root_project_context=root_project_context,
            workspace_context=workspace_context,
        )
        mock_check_lint.assert_called_once_with(config=config)


class TestCheckProjectLint:
    def test_delegates_to_check_lint(
        self,
        root_project_context: ProjectContext,
        workspace_context: WorkspaceContext,
        mocker: MockerFixture,
    ) -> None:
        target_project_context = workspace_context.get_project_context("project-b")
        assert target_project_context is not None
        config = RuffCheckConfig(
            target=target_project_context.project_root,
            working_directory=root_project_context.project_root,
        )
        expected = Success(RuffCheckResult(name=str(config.target), diagnostics=()))

        mock_for_project = mocker.patch(
            "gyomu_python_analysis.tools.ruff.check.for_project",
            return_value=config,
        )
        mock_check_lint = mocker.patch(
            "gyomu_python_analysis.tools.ruff.check._check_lint",
            return_value=expected,
        )

        actual = check_project_lint(
            target_project_context=target_project_context,
            workspace_root_project_context=root_project_context,
            workspace_context=workspace_context,
        )

        assert actual == expected
        mock_for_project.assert_called_once_with(
            target_project_context=target_project_context,
            workspace_root_project_context=root_project_context,
            workspace_context=workspace_context,
        )
        mock_check_lint.assert_called_once_with(config=config)


class TestCheckWorkspaceLint:
    def test_delegates_to_check_lint(
        self,
        workspace_context: WorkspaceContext,
        mocker: MockerFixture,
    ) -> None:
        config = RuffCheckConfig(
            target=workspace_context.workspace_root.path,
            working_directory=workspace_context.workspace_root.path,
        )
        expected = Success(RuffCheckResult(name=str(config.target), diagnostics=()))

        mock_for_workspace = mocker.patch(
            "gyomu_python_analysis.tools.ruff.check.for_workspace",
            return_value=config,
        )
        mock_check_lint = mocker.patch(
            "gyomu_python_analysis.tools.ruff.check._check_lint",
            return_value=expected,
        )

        actual = check_workspace_lint(workspace_context=workspace_context)

        assert actual == expected
        mock_for_workspace.assert_called_once_with(
            workspace_context=workspace_context,
        )
        mock_check_lint.assert_called_once_with(config=config)
