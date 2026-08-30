from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock, Mock
from uuid import UUID

import pytest
from gyomu_schema.error import DatabaseError
from gyomu_schema.error.validation import ValidationError
from gyomu_schema.gyomu.user import User
from gyomu_schema.parameter.parameter_master import (
    ParameterMaster,
    ParameterMasterCreate,
    ParameterMasterUpdate,
)
from returns.result import Failure, Success
from sqlalchemy.orm import Session
from uuid6 import uuid7

from gyomu_infra.db.repository.parameter_master import ParameterMasterRepository
from gyomu_infra.gyomu.parameter.parameter_access import (
    ParameterAccessImpl,
    create_parameter_access,
)


def make_parameter(
    *,
    item_key: str = "test_key",
    item_value: str = "test_value",
    item_fromdate: str | None = None,
) -> ParameterMaster:
    return ParameterMaster(
        id=uuid7(),
        item_key=item_key,
        item_value=item_value,
        item_fromdate=item_fromdate,
    )


test_uuid = uuid7()


def make_parameter_with_id(
    *,
    id: UUID = test_uuid,
    item_key: str = "test_key",
    item_value: str = "test_value",
    item_fromdate: str | None = None,
) -> ParameterMaster:
    return ParameterMaster(
        id=id,
        item_key=item_key,
        item_value=item_value,
        item_fromdate=item_fromdate,
    )


@pytest.fixture
def transaction() -> MagicMock:
    transaction = MagicMock()
    transaction.__enter__.return_value = transaction
    return transaction


@pytest.fixture
def repository(
    transaction: MagicMock,
) -> ParameterMasterRepository:
    repository = MagicMock(spec=ParameterMasterRepository)
    repository.transaction.return_value = transaction
    return repository


class TestParameterAccess_GetItemKey:
    def test_returns_key_when_user_is_none(
        self,
        repository: MagicMock,
    ) -> None:
        access = ParameterAccessImpl(repository)

        result = access._get_item_key("test_key")

        assert result == "test_key"

    def test_returns_user_scoped_key_when_user_is_given(
        self,
        repository: MagicMock,
    ) -> None:
        access = ParameterAccessImpl(repository)
        user = User(user_id="user123")

        result = access._get_item_key("test_key", user)

        assert result == "user123_test_key"


class TestParameterAccess_GetValue:
    def test_returns_first_parameter_when_target_date_is_none(
        self,
        repository: MagicMock,
    ) -> None:
        repository.find_by_item_key.return_value = Success(
            [
                make_parameter(
                    item_value="first",
                    item_fromdate=None,
                ),
                make_parameter(
                    item_value="second",
                    item_fromdate="2025-01-01",
                ),
            ]
        )

        access = ParameterAccessImpl(repository)

        result = access.get_value("test_key")

        assert result == Success("first")
        repository.find_by_item_key.assert_called_once_with("test_key")

    def test_uses_user_scoped_key(
        self,
        repository: MagicMock,
    ) -> None:
        repository.find_by_item_key.return_value = Success(
            [
                make_parameter(
                    item_key="user123_test_key",
                    item_value="user-value",
                ),
            ]
        )

        access = ParameterAccessImpl(repository)
        user = User(user_id="user123")

        result = access.get_value("test_key", user)

        assert result == Success("user-value")
        repository.find_by_item_key.assert_called_once_with("user123_test_key")

    def test_returns_default_value_when_target_date_is_before_first_effective_date(
        self,
        repository: MagicMock,
    ) -> None:
        repository.find_by_item_key.return_value = Success(
            [
                make_parameter(
                    item_value="default",
                    item_fromdate=None,
                ),
                make_parameter(
                    item_value="2025-value",
                    item_fromdate="2025-01-01",
                ),
            ]
        )

        access = ParameterAccessImpl(repository)

        result = access.get_value(
            "test_key",
            target_date=date(2024, 12, 31),
        )

        assert result == Success("default")

    def test_returns_value_when_target_date_matches_effective_date(
        self,
        repository: MagicMock,
    ) -> None:
        repository.find_by_item_key.return_value = Success(
            [
                make_parameter(
                    item_value="default",
                    item_fromdate=None,
                ),
                make_parameter(
                    item_value="2025-value",
                    item_fromdate="2025-01-01",
                ),
            ]
        )

        access = ParameterAccessImpl(repository)

        result = access.get_value(
            "test_key",
            target_date=date(2025, 1, 1),
        )

        assert result == Success("2025-value")

    def test_returns_latest_value_before_target_date(
        self,
        repository: MagicMock,
    ) -> None:
        repository.find_by_item_key.return_value = Success(
            [
                make_parameter(
                    item_value="default",
                    item_fromdate=None,
                ),
                make_parameter(
                    item_value="2024-value",
                    item_fromdate="2024-01-01",
                ),
                make_parameter(
                    item_value="2025-value",
                    item_fromdate="2025-01-01",
                ),
            ]
        )

        access = ParameterAccessImpl(repository)

        result = access.get_value(
            "test_key",
            target_date=date(2024, 6, 1),
        )

        assert result == Success("2024-value")

    def test_returns_latest_value_when_target_date_is_after_multiple_effective_dates(
        self,
        repository: MagicMock,
    ) -> None:
        repository.find_by_item_key.return_value = Success(
            [
                make_parameter(
                    item_value="default",
                    item_fromdate=None,
                ),
                make_parameter(
                    item_value="2024-value",
                    item_fromdate="2024-01-01",
                ),
                make_parameter(
                    item_value="2025-value",
                    item_fromdate="2025-01-01",
                ),
            ]
        )

        access = ParameterAccessImpl(repository)

        result = access.get_value(
            "test_key",
            target_date=date(2026, 1, 1),
        )

        assert result == Success("2025-value")

    def test_returns_database_error_when_parameter_does_not_exist(
        self,
        repository: MagicMock,
    ) -> None:
        repository.find_by_item_key.return_value = Success([])

        access = ParameterAccessImpl(repository)

        result = access.get_value("test_key")

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), DatabaseError)

    def test_returns_database_error_when_default_does_not_exist(
        self,
        repository: MagicMock,
    ) -> None:
        repository.find_by_item_key.return_value = Success(
            [
                make_parameter(
                    item_value="2025-value",
                    item_fromdate="2025-01-01",
                ),
            ]
        )

        access = ParameterAccessImpl(repository)

        result = access.get_value(
            "test_key",
            target_date=date(2025, 6, 1),
        )

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), DatabaseError)

    def test_returns_database_error_when_multiple_defaults_exist(
        self,
        repository: MagicMock,
    ) -> None:
        repository.find_by_item_key.return_value = Success(
            [
                make_parameter(
                    item_value="default-1",
                    item_fromdate=None,
                ),
                make_parameter(
                    item_value="default-2",
                    item_fromdate=None,
                ),
            ]
        )

        access = ParameterAccessImpl(repository)

        result = access.get_value(
            "test_key",
            target_date=date(2025, 6, 1),
        )

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), DatabaseError)

    def test_propagates_repository_failure(
        self,
        repository: MagicMock,
    ) -> None:
        error = DatabaseError("database error")
        repository.find_by_item_key.return_value = Failure(error)

        access = ParameterAccessImpl(repository)

        result = access.get_value("test_key")

        assert result == Failure(error)

    def test_returns_latest_effective_value_before_target_date(
        self,
        repository: MagicMock,
    ) -> None:
        repository.find_by_item_key.return_value = Success(
            [
                make_parameter(
                    item_value="default",
                    item_fromdate=None,
                ),
                make_parameter(
                    item_value="2024-value",
                    item_fromdate="2024-01-01",
                ),
                make_parameter(
                    item_value="2025-value",
                    item_fromdate="2025-01-01",
                ),
                make_parameter(
                    item_value="2026-value",
                    item_fromdate="2026-01-01",
                ),
            ]
        )

        access = ParameterAccessImpl(repository)

        result = access.get_value(
            "test_key",
            target_date=date(2025, 12, 31),
        )

        assert result == Success("2025-value")

    def test_returns_value_when_target_date_matches_latest_effective_date(
        self,
        repository: MagicMock,
    ) -> None:
        repository.find_by_item_key.return_value = Success(
            [
                make_parameter(
                    item_value="default",
                    item_fromdate=None,
                ),
                make_parameter(
                    item_value="2024-value",
                    item_fromdate="2024-01-01",
                ),
                make_parameter(
                    item_value="2025-value",
                    item_fromdate="2025-01-01",
                ),
                make_parameter(
                    item_value="2026-value",
                    item_fromdate="2026-01-01",
                ),
            ]
        )

        access = ParameterAccessImpl(repository)

        result = access.get_value(
            "test_key",
            target_date=date(2025, 1, 1),
        )

        assert result == Success("2025-value")


class TestParameterAccess_KeyExists:
    def test_returns_true_when_parameter_exists(
        self,
        repository: MagicMock,
    ) -> None:
        repository.find_by_item_key.return_value = Success(
            [
                make_parameter(
                    item_value="test",
                    item_fromdate=None,
                )
            ]
        )

        access = ParameterAccessImpl(repository)

        result = access.key_exists("test_key")

        assert result == Success(True)
        repository.find_by_item_key.assert_called_once_with("test_key")

    def test_returns_false_when_parameter_does_not_exist(
        self,
        repository: MagicMock,
    ) -> None:
        repository.find_by_item_key.return_value = Success([])

        access = ParameterAccessImpl(repository)

        result = access.key_exists("test_key")

        assert result == Success(False)
        repository.find_by_item_key.assert_called_once_with("test_key")

    def test_returns_failure_when_repository_returns_failure(self) -> None:
        repository = MagicMock(spec=ParameterMasterRepository)

        error = DatabaseError(
            message="Database error",
        )
        repository.find_by_item_key.return_value = Failure(error)

        access = ParameterAccessImpl(repository)

        result = access.key_exists("test_key")

        assert result == Failure(error)
        repository.find_by_item_key.assert_called_once_with("test_key")

    def test_uses_user_id_in_item_key(self) -> None:
        repository = MagicMock(spec=ParameterMasterRepository)
        repository.find_by_item_key.return_value = Success(
            [
                make_parameter(
                    item_value="test",
                    item_fromdate=None,
                )
            ]
        )

        access = ParameterAccessImpl(repository)

        user = User(user_id="user123")

        result = access.key_exists("test_key", user)

        assert result == Success(True)
        repository.find_by_item_key.assert_called_once_with("user123_test_key")


class TestParameterAccess_SetValue:
    def test_inserts_parameter_when_key_does_not_exist(
        self,
        repository: MagicMock,
    ) -> None:
        repository.find_by_item_key.return_value = Success([])
        repository.insert.return_value = Success(
            make_parameter(
                item_value="new_value",
                item_fromdate=None,
            )
        )

        access = ParameterAccessImpl(repository)

        result = access.set_value("test_key", "new_value")

        assert result == Success(None)
        repository.find_by_item_key.assert_called_once_with("test_key")
        repository.insert.assert_called_once_with(
            ParameterMasterCreate(
                item_key="test_key",
                item_value="new_value",
                item_fromdate=None,
            )
        )
        repository.update.assert_not_called()
        repository.delete.assert_not_called()

    def test_does_nothing_when_key_does_not_exist_and_value_is_empty(
        self,
        repository: MagicMock,
    ) -> None:
        repository.find_by_item_key.return_value = Success([])

        access = ParameterAccessImpl(repository)

        result = access.set_value("test_key", "")

        assert result == Success(None)
        repository.find_by_item_key.assert_called_once_with("test_key")
        repository.insert.assert_not_called()
        repository.update.assert_not_called()
        repository.delete.assert_not_called()

    def test_updates_parameter_when_key_exists(
        self,
        repository: MagicMock,
    ) -> None:
        parameter = make_parameter(
            item_value="old_value",
            item_fromdate=None,
        )

        repository.find_by_item_key.return_value = Success([parameter])
        repository.update.return_value = Success(
            make_parameter_with_id(
                id=parameter.id,
                item_value="new_value",
                item_fromdate=None,
            )
        )

        access = ParameterAccessImpl(repository)

        result = access.set_value("test_key", "new_value")

        assert result == Success(None)
        repository.find_by_item_key.assert_called_once_with("test_key")
        repository.update.assert_called_once_with(
            ParameterMasterUpdate(
                id=parameter.id,
                item_value="new_value",
            )
        )
        repository.insert.assert_not_called()
        repository.delete.assert_not_called()

    def test_deletes_parameter_when_key_exists_and_value_is_empty(
        self,
        repository: MagicMock,
    ) -> None:
        parameter = make_parameter(
            item_value="old_value",
            item_fromdate=None,
        )

        repository.find_by_item_key.return_value = Success([parameter])
        repository.delete.return_value = Success(None)

        access = ParameterAccessImpl(repository)

        result = access.set_value("test_key", "")

        assert result == Success(None)
        repository.find_by_item_key.assert_called_once_with("test_key")
        repository.delete.assert_called_once_with(parameter.id)
        repository.insert.assert_not_called()
        repository.update.assert_not_called()

    def test_uses_user_id_in_item_key(
        self,
        repository: MagicMock,
    ) -> None:
        user = User(user_id="user123")

        repository.find_by_item_key.return_value = Success([])
        repository.insert.return_value = Success(
            make_parameter(
                item_value="new_value",
                item_fromdate=None,
            )
        )

        access = ParameterAccessImpl(repository)

        result = access.set_value("test_key", "new_value", user)

        assert result == Success(None)
        repository.find_by_item_key.assert_called_once_with("user123_test_key")
        repository.insert.assert_called_once_with(
            ParameterMasterCreate(
                item_key="user123_test_key",
                item_value="new_value",
                item_fromdate=None,
            )
        )

    def test_returns_failure_when_find_fails(
        self,
        repository: MagicMock,
        transaction: MagicMock,
    ) -> None:
        error = DatabaseError(
            message="Database error",
        )

        repository.find_by_item_key.return_value = Failure(error)

        access = ParameterAccessImpl(repository)

        result = access.set_value("test_key", "new_value")

        assert result == Failure(error)
        repository.insert.assert_not_called()
        repository.update.assert_not_called()
        repository.delete.assert_not_called()

        transaction.rollback.assert_called_once()

    def test_rolls_back_when_insert_fails(
        self,
        repository: MagicMock,
        transaction: MagicMock,
    ) -> None:
        error = DatabaseError(
            message="Database error",
        )

        repository.find_by_item_key.return_value = Success([])
        repository.insert.return_value = Failure(error)

        access = ParameterAccessImpl(repository)

        result = access.set_value("test_key", "new_value")

        assert result == Failure(error)
        transaction.rollback.assert_called_once()

    def test_rolls_back_when_update_fails(
        self,
        repository: MagicMock,
        transaction: MagicMock,
    ) -> None:
        parameter = make_parameter(
            item_value="old_value",
            item_fromdate=None,
        )

        error = DatabaseError(
            message="Database error",
        )

        repository.find_by_item_key.return_value = Success([parameter])
        repository.update.return_value = Failure(error)

        access = ParameterAccessImpl(repository)

        result = access.set_value("test_key", "new_value")

        assert result == Failure(error)
        transaction.rollback.assert_called_once()

    def test_rolls_back_when_delete_fails(
        self,
        repository: MagicMock,
        transaction: MagicMock,
    ) -> None:
        parameter = make_parameter(
            item_value="old_value",
            item_fromdate=None,
        )

        error = DatabaseError(
            message="Database error",
        )

        repository.find_by_item_key.return_value = Success([parameter])
        repository.delete.return_value = Failure(error)

        access = ParameterAccessImpl(repository)

        result = access.set_value("test_key", "")

        assert result == Failure(error)
        transaction.rollback.assert_called_once()


class TestParameterAccessFactory:
    def test_creates_parameter_access(self) -> None:
        session = Mock(spec=Session)

        service = create_parameter_access(session)

        assert isinstance(service, ParameterAccessImpl)


class TestParameterAccess_GetBoolValue:
    def test_returns_true_when_value_is_true(
        self,
        repository: MagicMock,
    ) -> None:
        repository.find_by_item_key.return_value = Success(
            [
                make_parameter(
                    item_value="true",
                    item_fromdate=None,
                )
            ]
        )

        access = ParameterAccessImpl(repository)

        result = access.get_bool_value("test_key")

        assert result == Success(True)
        repository.find_by_item_key.assert_called_once_with("test_key")

    def test_returns_true_when_value_is_uppercase_true(
        self,
        repository: MagicMock,
    ) -> None:
        repository.find_by_item_key.return_value = Success(
            [
                make_parameter(
                    item_value="TRUE",
                    item_fromdate=None,
                )
            ]
        )

        access = ParameterAccessImpl(repository)

        result = access.get_bool_value("test_key")

        assert result == Success(True)

    def test_returns_true_when_value_is_mixed_case_true(
        self,
        repository: MagicMock,
    ) -> None:
        repository.find_by_item_key.return_value = Success(
            [
                make_parameter(
                    item_value="TrUe",
                    item_fromdate=None,
                )
            ]
        )

        access = ParameterAccessImpl(repository)

        result = access.get_bool_value("test_key")

        assert result == Success(True)

    def test_returns_false_when_value_is_false(
        self,
        repository: MagicMock,
    ) -> None:
        repository.find_by_item_key.return_value = Success(
            [
                make_parameter(
                    item_value="false",
                    item_fromdate=None,
                )
            ]
        )

        access = ParameterAccessImpl(repository)

        result = access.get_bool_value("test_key")

        assert result == Success(False)

    def test_returns_false_when_value_is_not_true(
        self,
        repository: MagicMock,
    ) -> None:
        repository.find_by_item_key.return_value = Success(
            [
                make_parameter(
                    item_value="abc",
                    item_fromdate=None,
                )
            ]
        )

        access = ParameterAccessImpl(repository)

        result = access.get_bool_value("test_key")

        assert result == Success(False)

    def test_propagates_repository_failure(
        self,
        repository: MagicMock,
    ) -> None:
        error = DatabaseError(message="Database error")
        repository.find_by_item_key.return_value = Failure(error)

        access = ParameterAccessImpl(repository)

        result = access.get_bool_value("test_key")

        assert result == Failure(error)


class TestParameterAccess_GetIntValue:
    def test_returns_integer_value(
        self,
        repository: MagicMock,
    ) -> None:
        repository.find_by_item_key.return_value = Success(
            [
                make_parameter(
                    item_value="123",
                    item_fromdate=None,
                )
            ]
        )

        access = ParameterAccessImpl(repository)

        result = access.get_int_value("test_key")

        assert result == Success(123)
        repository.find_by_item_key.assert_called_once_with("test_key")

    def test_returns_negative_integer_value(
        self,
        repository: MagicMock,
    ) -> None:
        repository.find_by_item_key.return_value = Success(
            [
                make_parameter(
                    item_value="-123",
                    item_fromdate=None,
                )
            ]
        )

        access = ParameterAccessImpl(repository)

        result = access.get_int_value("test_key")

        assert result == Success(-123)

    def test_returns_zero(
        self,
        repository: MagicMock,
    ) -> None:
        repository.find_by_item_key.return_value = Success(
            [
                make_parameter(
                    item_value="0",
                    item_fromdate=None,
                )
            ]
        )

        access = ParameterAccessImpl(repository)

        result = access.get_int_value("test_key")

        assert result == Success(0)

    def test_returns_validation_error_when_value_is_not_integer(
        self,
        repository: MagicMock,
    ) -> None:
        repository.find_by_item_key.return_value = Success(
            [
                make_parameter(
                    item_value="abc",
                    item_fromdate=None,
                )
            ]
        )

        access = ParameterAccessImpl(repository)

        result = access.get_int_value("test_key")

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), ValidationError)

    def test_returns_validation_error_when_value_is_empty(
        self,
        repository: MagicMock,
    ) -> None:
        repository.find_by_item_key.return_value = Success(
            [
                make_parameter(
                    item_value="",
                    item_fromdate=None,
                )
            ]
        )

        access = ParameterAccessImpl(repository)

        result = access.get_int_value("test_key")

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), ValidationError)

    def test_returns_validation_error_when_value_is_decimal(
        self,
        repository: MagicMock,
    ) -> None:
        repository.find_by_item_key.return_value = Success(
            [
                make_parameter(
                    item_value="123.45",
                    item_fromdate=None,
                )
            ]
        )

        access = ParameterAccessImpl(repository)

        result = access.get_int_value("test_key")

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), ValidationError)

    def test_propagates_repository_failure(
        self,
        repository: MagicMock,
    ) -> None:
        error = DatabaseError(message="Database error")
        repository.find_by_item_key.return_value = Failure(error)

        access = ParameterAccessImpl(repository)

        result = access.get_int_value("test_key")

        assert result == Failure(error)


class TestParameterAccess_GetDecimalValue:
    def test_returns_decimal_value(
        self,
        repository: MagicMock,
    ) -> None:
        repository.find_by_item_key.return_value = Success(
            [
                make_parameter(
                    item_value="123.45",
                    item_fromdate=None,
                )
            ]
        )

        access = ParameterAccessImpl(repository)

        result = access.get_decimal_value("test_key")

        assert result == Success(Decimal("123.45"))
        repository.find_by_item_key.assert_called_once_with("test_key")

    def test_returns_negative_decimal_value(
        self,
        repository: MagicMock,
    ) -> None:
        repository.find_by_item_key.return_value = Success(
            [
                make_parameter(
                    item_value="-123.45",
                    item_fromdate=None,
                )
            ]
        )

        access = ParameterAccessImpl(repository)

        result = access.get_decimal_value("test_key")

        assert result == Success(Decimal("-123.45"))

    def test_returns_zero(
        self,
        repository: MagicMock,
    ) -> None:
        repository.find_by_item_key.return_value = Success(
            [
                make_parameter(
                    item_value="0",
                    item_fromdate=None,
                )
            ]
        )

        access = ParameterAccessImpl(repository)

        result = access.get_decimal_value("test_key")

        assert result == Success(Decimal(0))

    def test_returns_decimal_value_with_trailing_zeros(
        self,
        repository: MagicMock,
    ) -> None:
        repository.find_by_item_key.return_value = Success(
            [
                make_parameter(
                    item_value="123.4500",
                    item_fromdate=None,
                )
            ]
        )

        access = ParameterAccessImpl(repository)

        result = access.get_decimal_value("test_key")

        assert result == Success(Decimal("123.4500"))

    def test_returns_validation_error_when_value_is_invalid(
        self,
        repository: MagicMock,
    ) -> None:
        repository.find_by_item_key.return_value = Success(
            [
                make_parameter(
                    item_value="abc",
                    item_fromdate=None,
                )
            ]
        )

        access = ParameterAccessImpl(repository)

        result = access.get_decimal_value("test_key")

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), ValidationError)

    def test_returns_validation_error_when_value_is_empty(
        self,
        repository: MagicMock,
    ) -> None:
        repository.find_by_item_key.return_value = Success(
            [
                make_parameter(
                    item_value="",
                    item_fromdate=None,
                )
            ]
        )

        access = ParameterAccessImpl(repository)

        result = access.get_decimal_value("test_key")

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), ValidationError)

    def test_propagates_repository_failure(
        self,
        repository: MagicMock,
    ) -> None:
        error = DatabaseError(message="Database error")
        repository.find_by_item_key.return_value = Failure(error)

        access = ParameterAccessImpl(repository)

        result = access.get_decimal_value("test_key")

        assert result == Failure(error)
