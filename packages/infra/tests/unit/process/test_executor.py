from pathlib import Path
from subprocess import CompletedProcess

from returns.result import Failure, Success

from gyomu_infra.process.error import ProcessError
from gyomu_infra.process.executor import execute
from gyomu_infra.process.model import ProcessResult


def test_execute_success() -> None:
    result = execute(
        (
            "python",
            "-c",
            "print('hello')",
        )
    )

    assert isinstance(result, Success)
    assert result.unwrap() == ProcessResult(
        exit_code=0,
        stdout="hello\n",
        stderr="",
    )


def test_execute_non_zero_exit_code() -> None:
    result = execute(
        (
            "python",
            "-c",
            "import sys; print('failed'); sys.exit(3)",
        )
    )

    assert isinstance(result, Success)
    assert result.unwrap() == ProcessResult(
        exit_code=3,
        stdout="failed\n",
        stderr="",
    )


def test_execute_captures_stderr() -> None:
    result = execute(
        (
            "python",
            "-c",
            "import sys; print('error', file=sys.stderr)",
        )
    )

    assert isinstance(result, Success)
    assert result.unwrap() == ProcessResult(
        exit_code=0,
        stdout="",
        stderr="error\n",
    )


def test_execute_passes_cwd(tmp_path: Path) -> None:
    result = execute(
        (
            "python",
            "-c",
            "from pathlib import Path; print(Path.cwd())",
        ),
        cwd=tmp_path,
    )

    assert isinstance(result, Success)
    assert result.unwrap().stdout.strip() == str(tmp_path)


def test_execute_fails_when_process_cannot_be_started() -> None:
    command = ("command-that-does-not-exist",)

    result = execute(command)

    assert isinstance(result, Failure)

    error = result.failure()
    assert isinstance(error, ProcessError)
    assert error.command == command
    assert error.exit_code is None


def test_execute_invokes_subprocess_run(mocker) -> None:
    run = mocker.patch(
        "gyomu_infra.process.executor.run",
        return_value=CompletedProcess(
            args=("ruff", "format", "example.py"),
            returncode=0,
            stdout="1 file reformatted\n",
            stderr="",
        ),
    )

    result = execute(
        ("ruff", "format", "example.py"),
        cwd=Path("/project"),
    )

    assert isinstance(result, Success)
    assert result.unwrap() == ProcessResult(
        exit_code=0,
        stdout="1 file reformatted\n",
        stderr="",
    )

    run.assert_called_once_with(
        ("ruff", "format", "example.py"),
        cwd=Path("/project"),
        capture_output=True,
        text=True,
        check=False,
    )


def test_execute_converts_os_error_to_process_error(mocker) -> None:
    mocker.patch(
        "gyomu_infra.process.executor.run",
        side_effect=FileNotFoundError("ruff not found"),
    )

    command = ("ruff", "format", "example.py")

    result = execute(command)

    assert isinstance(result, Failure)

    error = result.failure()
    assert isinstance(error, ProcessError)
    assert error.command == command
    assert error.exit_code is None
    assert error.details == {
        "exception": "FileNotFoundError",
    }
