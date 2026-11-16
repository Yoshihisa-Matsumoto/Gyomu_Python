from dataclasses import dataclass
from subprocess import Popen


@dataclass(frozen=True)
class ProcessResult:
    """Represents the result of an executed process, including its exit code,
    standard output, and standard error.
    """

    exit_code: int
    """The exit code returned by the process."""

    stdout: str
    """The standard output captured from the process."""

    stderr: str
    """The standard error captured from the process."""


@dataclass(frozen=True)
class ProcessHandle:
    process: Popen[str]
