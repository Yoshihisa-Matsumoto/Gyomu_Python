from collections.abc import AsyncIterator


def simple_for(values: list[int]) -> int:
    total = 0

    for value in values:
        total += value

    return total


def for_with_else(values: list[int]) -> int:
    total = 0

    for value in values:
        total += value
    else:
        total += 1

    return total


def for_with_break(values: list[int]) -> int:
    total = 0

    for value in values:
        if value < 0:
            break
        total += value

    return total


def nested_for(values: list[list[int]]) -> int:
    total = 0

    for items in values:
        for value in items:
            total += value

    return total


class AsyncValues:
    def __init__(self, values: list[int]) -> None:
        self.values = values

    def __aiter__(self) -> AsyncIterator[int]:
        return self._iterate()

    async def _iterate(self) -> AsyncIterator[int]:
        for value in self.values:
            yield value


async def async_for(values: AsyncValues) -> int:
    total = 0

    async for value in values:
        total += value

    return total
