from pathlib import Path
from subprocess import CompletedProcess, Popen

from returns.result import Failure, Success

from gyomu_infra.process.error import ProcessError
from gyomu_infra.process.executor import execute, execute_background
from gyomu_infra.process.model import ProcessHandle, ProcessResult


class TestExecute:
    def test_success(self) -> None:
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

    def test_non_zero_exit_code(self) -> None:
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

    def test_captures_stderr(self) -> None:
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

    def test_passes_cwd(self, tmp_path: Path) -> None:
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

    def test_fails_when_process_cannot_be_started(self) -> None:
        command = ("command-that-does-not-exist",)

        result = execute(command)

        assert isinstance(result, Failure)

        error = result.failure()
        assert isinstance(error, ProcessError)
        assert error.command == command
        assert error.exit_code is None

    def test_invokes_subprocess_run(self, mocker) -> None:
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

    def test_converts_os_error_to_process_error(self, mocker) -> None:
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


class TestExecuteBackground:
    def test_success(self, mocker) -> None:
        process = mocker.Mock(spec=Popen)
        popen = mocker.patch(
            "gyomu_infra.process.executor.Popen",
            return_value=process,
        )

        command = ("code", "example.json")

        result = execute_background(command)

        assert isinstance(result, Success)
        assert result.unwrap() == ProcessHandle(process=process)

        popen.assert_called_once_with(
            command,
            cwd=None,
            text=True,
        )

    def test_fails_when_process_cannot_be_started(self, mocker) -> None:
        mocker.patch(
            "gyomu_infra.process.executor.Popen",
            side_effect=FileNotFoundError("editor not found"),
        )

        command = ("editor-that-does-not-exist",)

        result = execute_background(command)

        assert isinstance(result, Failure)

        error = result.failure()
        assert isinstance(error, ProcessError)
        assert error.command == command
        assert error.exit_code is None
        assert error.details == {
            "exception": "FileNotFoundError",
        }

    def test_passes_cwd(self, mocker, tmp_path: Path) -> None:
        process = mocker.Mock()
        popen = mocker.patch(
            "gyomu_infra.process.executor.Popen",
            return_value=process,
        )

        result = execute_background(
            ("code", "example.json"),
            cwd=tmp_path,
        )

        assert isinstance(result, Success)
        assert result.unwrap() == ProcessHandle(process=process)

        popen.assert_called_once_with(
            ("code", "example.json"),
            cwd=tmp_path,
            text=True,
        )
