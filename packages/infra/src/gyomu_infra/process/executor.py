import os
from collections.abc import Mapping, Sequence
from pathlib import Path
from subprocess import CompletedProcess, Popen, run

from returns.result import Failure, Result, Success

from gyomu_infra.process.error import ProcessError
from gyomu_infra.process.model import ProcessHandle, ProcessResult


def execute(
    command: Sequence[str],
    *,
    cwd: Path | None = None,
    env: Mapping[str, str] | None = None,
) -> Result[ProcessResult, ProcessError]:
    """Execute a command and return its result.

    Executes a command and returns a Result containing either the ProcessResult on
    success or a ProcessError on failure.

    Args:
        command (Sequence[str]): The command and its arguments to execute.
        cwd (Path | None): The working directory in which to execute the command.

    Returns:
        Result[ProcessResult, ProcessError]: A Result containing a ProcessResult on
            success or a ProcessError on failure.
    """
    command_tuple = tuple(command)

    process_env = os.environ.copy()
    if env is not None:
        process_env.update(env)

    try:
        completed_process: CompletedProcess[str] = run(
            command_tuple,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            env=process_env,
        )
    except OSError as error:
        return Failure(
            ProcessError(
                str(error),
                command=command_tuple,
                exit_code=None,
                details={
                    "exception": type(error).__name__,
                },
            )
        )

    return Success(
        ProcessResult(
            exit_code=completed_process.returncode,
            stdout=completed_process.stdout,
            stderr=completed_process.stderr,
        )
    )


def execute_background(
    command: Sequence[str],
    *,
    cwd: Path | None = None,
    env: Mapping[str, str] | None = None,
) -> Result[ProcessHandle, ProcessError]:
    command_tuple = tuple(command)

    process_env = os.environ.copy()
    if env is not None:
        process_env.update(env)

    try:
        process = Popen(command_tuple, cwd=cwd, text=True, env=process_env)
    except OSError as error:
        return Failure(
            ProcessError(
                str(error),
                command=command_tuple,
                exit_code=None,
                details={"exception": type(error).__name__},
            )
        )

    return Success(ProcessHandle(process=process))
