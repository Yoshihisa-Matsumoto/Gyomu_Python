from types import TracebackType
from typing import Protocol, Self

from gyomu_schema.error.io import GyomuIOError
from returns.result import Result


class TransactionManager(Protocol):
    def rollback(self) -> Result[None, GyomuIOError]: ...

    def create_child(self) -> Result[TransactionManager, GyomuIOError]: ...

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...
