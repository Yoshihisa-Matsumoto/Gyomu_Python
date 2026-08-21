from types import TracebackType
from unittest.mock import MagicMock

from returns.result import Failure, Success
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from gyomu_infra.db.transaction.sqlalchemy_transaction_manager import (
    SqlAlchemyTransactionManager,
)


class TestSqlAlchemyTransactionManager_Init:
    def test_begin_root_transaction(self) -> None:
        session = MagicMock(spec=Session)
        transaction = MagicMock()
        session.begin.return_value = transaction

        manager = SqlAlchemyTransactionManager(session, None)

        session.begin.assert_called_once_with()
        session.begin_nested.assert_not_called()
        assert manager._transaction is transaction

    def test_begin_nested_transaction(self) -> None:
        session = MagicMock(spec=Session)
        transaction = MagicMock()
        session.begin_nested.return_value = transaction

        parent = MagicMock(spec=SqlAlchemyTransactionManager)

        manager = SqlAlchemyTransactionManager(session, parent)

        session.begin.assert_not_called()
        session.begin_nested.assert_called_once_with()
        assert manager._transaction is transaction


class TestSqlAlchemyTransactionManager_Enter:
    def test_enter_returns_self(self) -> None:
        session = MagicMock(spec=Session)
        transaction = MagicMock()
        session.begin.return_value = transaction

        manager = SqlAlchemyTransactionManager(session, None)

        result = manager.__enter__()

        assert result is manager


class TestSqlAlchemyTransactionManager_Exit:
    def test_exit_commits_when_no_exception(self) -> None:
        session = MagicMock(spec=Session)
        transaction = MagicMock()
        session.begin.return_value = transaction

        manager = SqlAlchemyTransactionManager(session, None)

        result = manager.__exit__(None, None, None)

        assert result is None
        transaction.commit.assert_called_once_with()
        transaction.rollback.assert_not_called()

    def test_exit_rolls_back_when_exception_occurs(self) -> None:
        session = MagicMock(spec=Session)
        transaction = MagicMock()
        session.begin.return_value = transaction

        manager = SqlAlchemyTransactionManager(session, None)

        exc = ValueError("test error")
        traceback = MagicMock(spec=TracebackType)

        result = manager.__exit__(
            ValueError,
            exc,
            traceback,
        )

        assert result is None
        transaction.rollback.assert_called_once_with()
        transaction.commit.assert_not_called()


class TestSqlAlchemyTransactionManager_Rollback:
    def test_rollback_returns_success(self) -> None:
        session = MagicMock(spec=Session)
        transaction = MagicMock()
        session.begin.return_value = transaction

        manager = SqlAlchemyTransactionManager(session, None)

        result = manager.rollback()

        assert isinstance(result, Success)
        assert result.unwrap() is None
        transaction.rollback.assert_called_once_with()

    def test_rollback_returns_failure_when_sqlalchemy_error_occurs(self) -> None:
        session = MagicMock(spec=Session)
        transaction = MagicMock()
        session.begin.return_value = transaction

        transaction.rollback.side_effect = SQLAlchemyError("rollback failed")

        manager = SqlAlchemyTransactionManager(session, None)

        result = manager.rollback()

        assert isinstance(result, Failure)
        assert result.failure().__class__.__name__ == "DatabaseError"

        transaction.rollback.assert_called_once_with()


class TestSqlAlchemyTransactionManager_CreateChild:
    def test_create_child_returns_child_transaction_manager(self) -> None:
        session = MagicMock(spec=Session)
        transaction = MagicMock()
        session.begin.return_value = transaction

        manager = SqlAlchemyTransactionManager(session, None)

        result = manager.create_child()

        assert isinstance(result, Success)

        child = result.unwrap()

        assert isinstance(child, SqlAlchemyTransactionManager)
        assert child._session is session

        session.begin_nested.assert_called_once_with()
