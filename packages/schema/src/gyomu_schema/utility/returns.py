from collections.abc import Awaitable, Callable

from returns.result import Failure, Result, Success


def from_sync[T, E: Exception](
    f: Callable[[], T],
    *,
    build_error: Callable[[Exception], E],
) -> Result[T, E]:
    try:
        return Success(f())
    except Exception as e:
        return Failure(build_error(e))


async def from_async[T, E: Exception](
    f: Callable[[], Awaitable[T]],
    *,
    build_error: Callable[[Exception], E],
) -> Result[T, E]:
    try:
        return Success(await f())
    except Exception as e:
        return Failure(build_error(e))
