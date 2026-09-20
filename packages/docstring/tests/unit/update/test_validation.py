from pathlib import Path

import pytest
from gyomu_docstring.error.update import UpdateError
from gyomu_docstring.update.validation import (
    run_ruff_check,
    run_ruff_format,
    validate_source,
)
from gyomu_infra.process.error import ProcessError
from gyomu_infra.process.model import ProcessResult
from gyomu_schema.schemas.python.file_analysis import FileAnalysisContext
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.schemas.types import FullPath
from returns.result import Failure, Success

from packages.schema.schema_test_support.helpers import create_file_analysis_context


@pytest.fixture
def file_context() -> FileAnalysisContext:
    return create_file_analysis_context()


def test_run_ruff_format_success(
    mocker,
    file_context: FileAnalysisContext,
) -> None:
    execute = mocker.patch(
        "gyomu_docstring.update.validation.execute",
        return_value=Success(
            ProcessResult(
                exit_code=0,
                stdout="1 file left unchanged\n",
                stderr="",
            )
        ),
    )

    result = run_ruff_format(
        ProjectRelativePath(Path("src/example.py")),
        project_root=FullPath(Path("/project")),
        file_context=file_context,
    )

    assert result == Success(None)

    execute.assert_called_once_with(
        ("ruff", "format", str(Path("src/example.py"))),
        cwd=Path("/project"),
    )


def test_run_ruff_format_failure(
    mocker,
    file_context: FileAnalysisContext,
) -> None:
    execute = mocker.patch(
        "gyomu_docstring.update.validation.execute",
        return_value=Success(
            ProcessResult(
                exit_code=1,
                stdout="",
                stderr="ruff format failed\n",
            )
        ),
    )

    result = run_ruff_format(
        ProjectRelativePath(Path("src/example.py")),
        project_root=FullPath(Path("/project")),
        file_context=file_context,
    )

    assert isinstance(result, Failure)

    error = result.failure()
    assert isinstance(error, UpdateError)
    assert error.details == {
        "exit_code": 1,
        "stdout": "",
        "stderr": "ruff format failed\n",
    }

    execute.assert_called_once_with(
        ("ruff", "format", str(Path("src/example.py"))),
        cwd=Path("/project"),
    )


def test_run_ruff_format_process_error(
    mocker,
    file_context: FileAnalysisContext,
) -> None:
    process_error = ProcessError(
        "ruff not found",
        command=("ruff", "format", "src/example.py"),
        exit_code=None,
    )

    mocker.patch(
        "gyomu_docstring.update.validation.execute",
        return_value=Failure(process_error),
    )

    result = run_ruff_format(
        ProjectRelativePath(Path("src/example.py")),
        project_root=FullPath(Path("/project")),
        file_context=file_context,
    )

    assert isinstance(result, Failure)

    error = result.failure()
    assert isinstance(error, UpdateError)

    assert error.message == "fail to execute ruff format"


def test_run_ruff_check_success(
    mocker,
    file_context: FileAnalysisContext,
) -> None:
    execute = mocker.patch(
        "gyomu_docstring.update.validation.execute",
        return_value=Success(
            ProcessResult(
                exit_code=0,
                stdout="All checks passed!\n",
                stderr="",
            )
        ),
    )

    result = run_ruff_check(
        ProjectRelativePath(Path("src/example.py")),
        project_root=FullPath(Path("/project")),
        file_context=file_context,
    )

    assert result == Success(None)

    execute.assert_called_once_with(
        ("ruff", "check", str(Path("src/example.py"))),
        cwd=Path("/project"),
    )


def test_run_ruff_check_failure(
    mocker,
    file_context: FileAnalysisContext,
) -> None:
    mocker.patch(
        "gyomu_docstring.update.validation.execute",
        return_value=Success(
            ProcessResult(
                exit_code=1,
                stdout="src/example.py:1:1: F401 ...\n",
                stderr="",
            )
        ),
    )

    result = run_ruff_check(
        ProjectRelativePath(Path("src/example.py")),
        project_root=FullPath(Path("/project")),
        file_context=file_context,
    )

    assert isinstance(result, Failure)

    error = result.failure()
    assert error.details == {
        "exit_code": 1,
        "stdout": "src/example.py:1:1: F401 ...\n",
        "stderr": "",
    }


def test_validate_source_does_not_check_when_format_fails(
    mocker,
    file_context: FileAnalysisContext,
) -> None:
    error = UpdateError(
        "ruff format failed",
        file_path=file_context.analysis.module_name,
        phase="post-update",
        identity=None,
        context="test",
    )

    mocker.patch(
        "gyomu_docstring.update.validation.run_ruff_format",
        return_value=Failure(error),
    )
    run_check = mocker.patch(
        "gyomu_docstring.update.validation.run_ruff_check",
    )

    result = validate_source(
        ProjectRelativePath(Path("src/example.py")),
        project_root=FullPath(Path("/project")),
        file_context=file_context,
    )

    assert result == Failure(error)
    run_check.assert_not_called()


def test_validate_source_returns_check_failure(
    mocker,
    file_context: FileAnalysisContext,
) -> None:
    error = UpdateError(
        "ruff check failed",
        file_path=file_context.analysis.module_name,
        phase="post-update",
        identity=None,
        context="test",
    )

    mocker.patch(
        "gyomu_docstring.update.validation.run_ruff_format",
        return_value=Success(None),
    )
    mocker.patch(
        "gyomu_docstring.update.validation.run_ruff_check",
        return_value=Failure(error),
    )

    result = validate_source(
        ProjectRelativePath(Path("src/example.py")),
        project_root=FullPath(Path("/project")),
        file_context=file_context,
    )

    assert result == Failure(error)
