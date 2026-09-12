from types import TracebackType
from typing import Protocol, Self

from gyomu_schema.error.database import DatabaseError
from returns.result import Result


class TransactionManager(Protocol):
    def rollback(self) -> Result[None, DatabaseError]: ...

    def create_child(self) -> Result[Self, DatabaseError]: ...

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...
