from collections.abc import Callable, Iterator
from typing import TypeVar

from returns.result import Failure, Result, Success

T = TypeVar("T")
U = TypeVar("U")
E = TypeVar("E")


class RecordStream[T, E]:
    """A lazy, single-use stream of Result values."""

    def __init__(
        self,
        iterator: Iterator[Result[T, E]],
    ) -> None:
        self._iterator = iterator

    @classmethod
    def from_iterator(
        cls,
        iterator: Iterator[Result[T, E]],
    ) -> RecordStream[T, E]:
        return cls(iterator)

    def __iter__(self) -> Iterator[Result[T, E]]:
        return self._iterator

    def map(
        self,
        fn: Callable[[T], U],
    ) -> RecordStream[U, E]:
        def iterator() -> Iterator[Result[U, E]]:
            for result in self._iterator:
                if isinstance(result, Success):
                    yield Success(fn(result.unwrap()))
                else:
                    yield Failure(result.failure())

        return RecordStream(iterator())

    def filter(
        self,
        predicate: Callable[[T], bool],
    ) -> RecordStream[T, E]:
        def iterator() -> Iterator[Result[T, E]]:
            for result in self._iterator:
                if isinstance(result, Success):
                    value = result.unwrap()
                    if predicate(value):
                        yield result
                else:
                    yield result

        return RecordStream(iterator())

    def tap(
        self,
        fn: Callable[[T], None],
    ) -> RecordStream[T, E]:
        def iterator() -> Iterator[Result[T, E]]:
            for result in self._iterator:
                if isinstance(result, Success):
                    fn(result.unwrap())
                yield result

        return RecordStream(iterator())

    def tap_failure(
        self,
        fn: Callable[[E], None],
    ) -> RecordStream[T, E]:
        def iterator() -> Iterator[Result[T, E]]:
            for result in self._iterator:
                if not isinstance(result, Success):
                    fn(result.failure())
                yield result

        return RecordStream(iterator())
