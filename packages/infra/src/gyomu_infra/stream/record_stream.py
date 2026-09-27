from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import TypeVar

from returns.result import Failure, Result, Success

T = TypeVar("T")
"""Type variable T."""

E = TypeVar("E")
"""Type variable E."""


Target = TypeVar("Target")
"""Target type variable."""

TargetError = TypeVar("TargetError")
"""Target error type variable."""


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
        """Create a RecordStream from an iterator of Result values.

        Create a RecordStream from an existing iterator of results.

        Returns:
            RecordStream[T, E]: A new RecordStream instance containing the given
                iterator.
        """
        return cls(iterator)

    def __iter__(self) -> Iterator[Result[T, E]]:
        """Iterate over the stream values.

        Return the underlying iterator.

        Returns:
            Iterator[Result[T, E]]: The underlying iterator of Result values.
        """
        return self._iterator

    def map(
        self,
        fn: Callable[[T], Target],
    ) -> RecordStream[Target, E]:
        """Transform successful values in the stream.

        Transform successful values in the stream using the provided function.

        Returns:
            RecordStream[Target, E]: A new RecordStream with transformed successful
                values.
        """

        def iterator() -> Iterator[Result[Target, E]]:
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
        """Filter successful values in the stream.

        Filter successful values in the stream using the provided predicate.

        Returns:
            RecordStream[T, E]: A new filtered RecordStream.
        """

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
        """Execute a side-effect on each successful value.

        Execute a side-effect function on each successful value without modifying the
        stream.

        Returns:
            RecordStream[T, E]: The same RecordStream instance for chaining.
        """

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
        """Execute a side-effect on each failure value.

        Execute a side-effect function on each failure value without modifying the
        stream.

        Returns:
            RecordStream[T, E]: The same RecordStream instance for chaining.
        """

        def iterator() -> Iterator[Result[T, E]]:
            for result in self._iterator:
                if not isinstance(result, Success):
                    fn(result.failure())
                yield result

        return RecordStream(iterator())

    def collect(self) -> list[Result[T, E]]:
        """Collect all results into a list.

        Consume the stream and collect all results into a list.

        Returns:
            list[Result[T, E]]: A list containing all Result values from the stream.
        """
        return list(self._iterator)

    def map_result(
        self,
        fn: Callable[[T], Result[Target, TargetError]],
    ) -> RecordStream[Target, E | TargetError]:
        """Transform successful values into new Result values.

        Transform successful values into new Results, potentially introducing new error
        types.

        Returns:
            RecordStream[Target, E | TargetError]: A new RecordStream with transformed
                Result values.
        """

        def iterator() -> Iterator[Result[Target, E | TargetError]]:
            for result in self._iterator:
                if isinstance(result, Success):
                    yield fn(result.unwrap())
                else:
                    yield Failure(result.failure())

        return RecordStream(iterator())

    def map_error(
        self,
        fn: Callable[[E], TargetError],
    ) -> RecordStream[T, TargetError]:
        """Transform error values in the stream.

        Transform failure errors in the stream using the provided function.

        Returns:
            RecordStream[T, TargetError]: A new RecordStream with transformed error
                types.
        """

        def iterator() -> Iterator[Result[T, TargetError]]:
            for result in self._iterator:
                if isinstance(result, Success):
                    yield result
                else:
                    yield Failure(fn(result.failure()))

        return RecordStream(iterator())
