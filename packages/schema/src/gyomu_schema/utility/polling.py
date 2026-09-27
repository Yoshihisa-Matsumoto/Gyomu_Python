import time
from collections.abc import Callable

from returns.result import Failure, Result, Success

from gyomu_schema.error.timeout import GyomuTimeoutError


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
        action_name (str): Name of the polling action.
        timeout_seconds (float): Maximum duration to continue polling.
        interval_seconds (float): Delay between polling attempts.
        action (Callable[[], bool]): Function to execute repeatedly.

    Returns:
        Result[bool, GyomuTimeoutError]: Success(True) if the action returns True within
            the timeout.
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
