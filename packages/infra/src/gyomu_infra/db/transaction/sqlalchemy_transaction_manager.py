from types import TracebackType
from typing import Self

from gyomu_schema.error.database import DatabaseError
from returns.result import Result, Success, safe
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from gyomu_infra.db.error.database import to_database_error


class SqlAlchemyTransactionManager:
    """Manages SQLAlchemy database transactions and nested savepoints."""

    def __init__(self, session: Session, parent: Self | None) -> None:
        self._session = session
        self._completed = False
        if parent is None:
            self._transaction = session.begin()
        else:
            self._transaction = session.begin_nested()

    def rollback(self) -> Result[None, DatabaseError]:
        """Rolls back the current transaction."""

        self._completed = True
        return self._rollback().alt(
            to_database_error,
        )

    @safe(exceptions=(SQLAlchemyError,))
    def _rollback(self) -> None:
        """Performs the underlying rollback operation."""

        self._transaction.rollback()

    def __enter__(self) -> Self:
        """Enters the runtime context for the transaction."""

        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Exits the runtime context, committing or rolling back based on exception
        state.
        """
        if self._completed:
            return

        if exc_type is not None:
            self._transaction.rollback()
            return

        self._transaction.commit()

    def create_child(self) -> Result[Self, DatabaseError]:
        """Creates a nested transaction manager child instance."""

        return Success(type(self)(self._session, self))
