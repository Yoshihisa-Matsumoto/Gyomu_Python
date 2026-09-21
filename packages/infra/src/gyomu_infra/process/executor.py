from collections.abc import Sequence
from pathlib import Path
from subprocess import CompletedProcess, run

from returns.result import Failure, Result, Success

from gyomu_infra.process.error import ProcessError
from gyomu_infra.process.model import ProcessResult


def execute(
    command: Sequence[str],
    *,
    cwd: Path | None = None,
) -> Result[ProcessResult, ProcessError]:
    command_tuple = tuple(command)

    try:
        completed_process: CompletedProcess[str] = run(
            command_tuple,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
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
