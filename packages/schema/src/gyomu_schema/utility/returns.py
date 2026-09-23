from collections.abc import Awaitable, Callable

from returns.result import Failure, Result, Success


def from_sync[T, E: Exception](
    f: Callable[[], T],
    *,
    build_error: Callable[[Exception], E],
) -> Result[T, E]:
    """Execute a synchronous function and wrap its outcome in a Result.

    Args:
        f (Callable[[], T]): Synchronous callable to execute.
        build_error (Callable[[Exception], E]): Function to convert caught exceptions to
            the desired error type.

    Returns:
        Result[T, E]: A Result containing either the success value or the built error.
    """
    try:
        return Success(f())
    except Exception as e:
        return Failure(build_error(e))


async def from_async[T, E: Exception](
    f: Callable[[], Awaitable[T]],
    *,
    build_error: Callable[[Exception], E],
) -> Result[T, E]:
    """Execute an asynchronous function and wrap its outcome in a Result.

    Args:
        f (Callable[[], Awaitable[T]]): Asynchronous callable to execute.
        build_error (Callable[[Exception], E]): Function to convert caught exceptions to
            the desired error type.

    Returns:
        Result[T, E]: A Result containing either the success value or the built error.
    """
    try:
        return Success(await f())
    except Exception as e:
        return Failure(build_error(e))
