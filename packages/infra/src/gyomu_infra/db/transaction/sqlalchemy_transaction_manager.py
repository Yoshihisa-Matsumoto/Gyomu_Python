from types import TracebackType
from typing import Self

from gyomu_schema.error.io import GyomuIOError
from returns.result import Result, Success, safe
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from gyomu_infra.db.error.database import to_database_error


class SqlAlchemyTransactionManager:
    def __init__(
        self, session: Session, parent: SqlAlchemyTransactionManager | None
    ) -> None:
        self._session = session
        self._completed = False
        if parent is None:
            self._transaction = session.begin()
        else:
            self._transaction = session.begin_nested()

    def rollback(self) -> Result[None, GyomuIOError]:
        self._completed = True
        return self._rollback().alt(
            to_database_error,
        )

    @safe(exceptions=(SQLAlchemyError,))
    def _rollback(self) -> None:
        self._transaction.rollback()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._completed:
            return

        if exc_type is not None:
            self._transaction.rollback()
            return

        self._transaction.commit()

    def create_child(self) -> Result[SqlAlchemyTransactionManager, GyomuIOError]:
        return Success(SqlAlchemyTransactionManager(self._session, self))
