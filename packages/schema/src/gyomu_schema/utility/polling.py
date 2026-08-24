import time
from collections.abc import Callable

from gyomu_schema.error.timeout import GyomuTimeoutError
from returns.result import Failure, Result, Success


def polling(
    action_name: str,
    timeout_seconds: float,
    interval_seconds: float,
    action: Callable[[], bool],
    *,
    clock: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
) -> Result[bool, GyomuTimeoutError]:
    """Poll an action until it succeeds or the timeout is reached.

    Args:
        action_name: Name of the polling action.
        timeout_seconds: Maximum duration to continue polling.
        interval_seconds: Delay between polling attempts.
        action: Function to execute repeatedly.

    Returns:
        Success(True) if the action returns True within the timeout.
        Failure(GyomuTimeoutError) if the timeout is reached.
    """
    start_time = clock()
    deadline = start_time + timeout_seconds

    while True:
        if action():
            return Success(True)

        if clock() >= deadline:
            return Failure(
                GyomuTimeoutError(
                    message=f"Timeout on polling: {action_name}",
                    action=action_name,
                    timeout_seconds=timeout_seconds,
                    interval_seconds=interval_seconds,
                    elapsed_seconds=clock() - start_time,
                )
            )

        sleep(interval_seconds)
