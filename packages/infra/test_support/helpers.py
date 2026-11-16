from collections.abc import Mapping

from gyomu_infra.process.error import ProcessError


def create_process_error(
    message: str = "test",
    command: tuple[str, ...] = (),
    exit_code: int | None = None,
    details: Mapping[str, object] | None = None,
) -> ProcessError:
    return ProcessError(
        message=message, command=command, exit_code=exit_code, details=details
    )
