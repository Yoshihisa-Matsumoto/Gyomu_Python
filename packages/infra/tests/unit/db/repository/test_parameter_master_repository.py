from unittest.mock import MagicMock

from gyomu_schema.error.database import DatabaseError
from gyomu_schema.error.validation import ValidationError
from gyomu_schema.parameter.parameter_master import (
    ParameterMaster,
    ParameterMasterCreate,
    ParameterMasterUpdate,
)
from returns.result import Failure, Success
from sqlalchemy import Delete, Select, Table
from sqlalchemy.exc import SQLAlchemyError
from uuid6 import uuid7

from gyomu_infra.db.mapper.parameter_master import to_schema
from gyomu_infra.db.model.generated.models import GyomuParamMaster
from gyomu_infra.db.repository.sqlalchemy_parameter_master import (
    SqlAlchemyParameterMasterRepository,
)


def make_model(
    *,
    id=None,
    item_key="test-key",
    item_value="test-value",
    item_fromdate=None,
) -> GyomuParamMaster:
    return GyomuParamMaster(
        id=id or uuid7(),
        item_key=item_key,
        item_value=item_value,
        item_fromdate=item_fromdate,
    )


def make_schema(model: GyomuParamMaster) -> ParameterMaster:
    return ParameterMaster.model_validate(
        model,
        from_attributes=True,
    )


class TestFindByItemParameterMaster:
    def test_returns_parameters(self) -> None:
        session = MagicMock()

        model = make_model()

        # Repositoryの実装に合わせてQuery/execute部分を設定

        session.scalars.return_value.all.return_value = [model]

        repository = SqlAlchemyParameterMasterRepository(session)

        result = repository.find_by_item_key("test-key")

        assert isinstance(result, Success)
        assert result.unwrap() == [make_schema(model)]

    def test_returns_multiple_parameters(self) -> None:
        session = MagicMock()

        models = [
            make_model(
                item_fromdate=None,
                item_value="default",
            ),
            make_model(
                item_fromdate="20260101",
                item_value="new",
            ),
            make_model(
                item_fromdate="20300101",
                item_value="future",
            ),
        ]

        session.scalars.return_value.all.return_value = models
        repository = SqlAlchemyParameterMasterRepository(session)

        result = repository.find_by_item_key("test-key")

        assert isinstance(result, Success)
        assert result.unwrap() == [make_schema(model) for model in models]

    def test_returns_empty_list(self) -> None:
        session = MagicMock()
        session.scalars.return_value.all.return_value = []
        repository = SqlAlchemyParameterMasterRepository(session)

        result = repository.find_by_item_key("unknown")

        assert isinstance(result, Success)
        assert result.unwrap() == []

    def test_find_by_item_key_returns_database_error(self) -> None:
        session = MagicMock()

        session.scalars.side_effect = SQLAlchemyError("database error")

        repository = SqlAlchemyParameterMasterRepository(session)

        result = repository.find_by_item_key("test-key")

        assert isinstance(result, Failure)

        error = result.failure()

        assert isinstance(error, DatabaseError)


def to_model_for_insert(schema: ParameterMasterCreate) -> GyomuParamMaster:
    return GyomuParamMaster(
        id=uuid7(),
        item_key=schema.item_key,
        item_value=schema.item_value,
        item_fromdate=schema.item_fromdate,
    )


class TestInsertParameterMaster:
    def test_returns_created_parameter(self) -> None:
        session = MagicMock()

        parameter = ParameterMasterCreate(
            item_key="test-key",
            item_value="test-value",
            item_fromdate=None,
        )

        session.execute.return_value.scalar_one.return_value = to_model_for_insert(
            parameter
        )

        repository = SqlAlchemyParameterMasterRepository(session)

        result = repository.insert(parameter)

        assert isinstance(result, Success)

        created = result.unwrap()

        assert created.item_key == parameter.item_key
        assert created.item_value == parameter.item_value
        assert created.item_fromdate is None

    def test_returns_database_error(self) -> None:
        session = MagicMock()
        parameter = ParameterMasterCreate(
            item_key="test-key",
            item_value="test-value",
            item_fromdate=None,
        )
        session.execute.side_effect = SQLAlchemyError("database error")

        repository = SqlAlchemyParameterMasterRepository(session)

        result = repository.insert(parameter)

        assert isinstance(result, Failure)

        error = result.failure()

        assert isinstance(error, DatabaseError)


TestUUID = uuid7()


class TestUpdateParameterMaster:
    def test_updates_all_specified_fields(self) -> None:
        session = MagicMock()

        update = ParameterMasterUpdate(
            id=TestUUID,
            item_key="new-key",
            item_value="new-value",
            item_fromdate="20260101",
        )

        rowResult = GyomuParamMaster(
            id=TestUUID,
            item_key=update.item_key,
            item_value=update.item_value,
            item_fromdate=update.item_fromdate,
        )
        session.execute.return_value.scalar_one.return_value = rowResult

        repository = SqlAlchemyParameterMasterRepository(session)

        result = repository.update(update)

        assert isinstance(result, Success)

        assert result.unwrap() == to_schema(rowResult)

        # passed data through session is
        # {
        #     "item_key": "new-key",
        #     "item_value": "new-value",
        #     "item_fromdate": "20260101",
        # }

    def test_only_updates_specified_fields(self) -> None:
        session = MagicMock()

        update = ParameterMasterUpdate(
            id=TestUUID,
            item_value="new-value",
        )
        rowResult = GyomuParamMaster(
            id=TestUUID,
            item_key="test-key",
            item_value=update.item_value,
        )

        session.execute.return_value.scalar_one.return_value = rowResult

        repository = SqlAlchemyParameterMasterRepository(session)
        result = repository.update(update)

        assert isinstance(result, Success)

        assert result.unwrap() == to_schema(rowResult)

        # UPDATE Statementを取得
        session.execute.assert_called_once()
        statement = session.execute.call_args.args[0]

        # UPDATE対象がitem_valueだけであることを確認
        updated_columns = {column.name for column in statement._values}

        assert updated_columns == {"item_value"}

        item_value_bind = statement._values[GyomuParamMaster.__table__.c.item_value]

        assert item_value_bind.value == "new-value"

    def test_only_updates_item_key(self) -> None:
        session = MagicMock()

        update = ParameterMasterUpdate(
            id=TestUUID,
            item_key="new-key",
        )

        row_result = GyomuParamMaster(
            id=TestUUID,
            item_key=update.item_key,
            item_value="test-value",
        )

        session.execute.return_value.scalar_one.return_value = row_result

        repository = SqlAlchemyParameterMasterRepository(session)
        result = repository.update(update)

        assert isinstance(result, Success)
        assert result.unwrap() == to_schema(row_result)

        # UPDATE Statementを取得
        session.execute.assert_called_once()
        statement = session.execute.call_args.args[0]

        # UPDATE対象がitem_keyだけであることを確認
        updated_columns = {column.name for column in statement._values}

        assert updated_columns == {"item_key"}

        # UPDATE値を確認
        item_key_bind = statement._values[GyomuParamMaster.__table__.c.item_key]

        assert item_key_bind.value == "new-key"

    def test_only_updates_item_fromdate(self) -> None:
        session = MagicMock()

        update = ParameterMasterUpdate(
            id=TestUUID,
            item_fromdate="20260101",
        )

        row_result = GyomuParamMaster(
            id=TestUUID,
            item_key="test-key",
            item_value="test-value",
            item_fromdate=update.item_fromdate,
        )

        session.execute.return_value.scalar_one.return_value = row_result

        repository = SqlAlchemyParameterMasterRepository(session)
        result = repository.update(update)

        assert isinstance(result, Success)
        assert result.unwrap() == to_schema(row_result)

        # UPDATE Statementを取得
        session.execute.assert_called_once()
        statement = session.execute.call_args.args[0]

        # UPDATE対象がitem_fromdateだけであることを確認
        updated_columns = {column.name for column in statement._values}

        assert updated_columns == {"item_fromdate"}

        # UPDATE値を確認
        item_fromdate_bind = statement._values[
            GyomuParamMaster.__table__.c.item_fromdate
        ]

        assert item_fromdate_bind.value == "20260101"

    def test_updates_multiple_specified_fields(self) -> None:
        session = MagicMock()

        update = ParameterMasterUpdate(
            id=TestUUID,
            item_key="new-key",
            item_value="new-value",
        )

        row_result = GyomuParamMaster(
            id=TestUUID,
            item_key=update.item_key,
            item_value=update.item_value,
            item_fromdate=None,
        )

        session.execute.return_value.scalar_one.return_value = row_result

        repository = SqlAlchemyParameterMasterRepository(session)
        result = repository.update(update)

        assert isinstance(result, Success)
        assert result.unwrap() == to_schema(row_result)

        # UPDATE Statementを取得
        session.execute.assert_called_once()
        statement = session.execute.call_args.args[0]

        # 指定した項目だけがUPDATE対象であることを確認
        updated_columns = {column.name for column in statement._values}

        assert updated_columns == {"item_key", "item_value"}

        # UPDATE値を確認
        item_key_bind = statement._values[GyomuParamMaster.__table__.c.item_key]
        item_value_bind = statement._values[GyomuParamMaster.__table__.c.item_value]

        assert item_key_bind.value == "new-key"
        assert item_value_bind.value == "new-value"

    def test_explicit_none_for_nullable_field(self) -> None:
        session = MagicMock()

        parameter_id = uuid7()

        update = ParameterMasterUpdate(
            id=parameter_id,
            item_fromdate=None,
        )

        # current = make_model(
        #     id=parameter_id,
        #     item_key="test-key",
        #     item_value="test-value",
        #     item_fromdate="20260101",
        # )

        updated = make_model(
            id=parameter_id,
            item_key="test-key",
            item_value="test-value",
            item_fromdate=None,
        )

        session.execute.return_value.scalar_one.return_value = updated

        repository = SqlAlchemyParameterMasterRepository(session)

        result = repository.update(update)

        assert isinstance(result, Success)
        assert result.unwrap() == make_schema(updated)

        # 明示的にNoneが指定されていることを確認
        assert update.model_dump(exclude_unset=True) == {
            "id": parameter_id,
            "item_fromdate": None,
        }

        # UPDATE Statementを取得
        session.execute.assert_called_once()
        statement = session.execute.call_args.args[0]

        # item_fromdateだけがUPDATE対象
        updated_columns = {column.name for column in statement._values}

        assert updated_columns == {"item_fromdate"}

        # NoneがUPDATE値として設定されていることを確認
        item_fromdate_bind = statement._values[
            GyomuParamMaster.__table__.c.item_fromdate
        ]

        assert item_fromdate_bind.value is None

    def test_with_empty_update_returns_current_parameter_without_update(
        self,
    ) -> None:
        session = MagicMock()

        parameter_id = uuid7()

        current = make_model(
            id=parameter_id,
            item_key="test-key",
            item_value="test-value",
            item_fromdate=None,
        )

        session.execute.return_value.scalar_one.return_value = current

        repository = SqlAlchemyParameterMasterRepository(session)

        result = repository.update(
            ParameterMasterUpdate(id=parameter_id),
        )

        assert isinstance(result, Success)
        assert result.unwrap() == make_schema(current)

        # DBアクセスは現在値を取得するSELECTだけ
        session.execute.assert_called_once()

        statement = session.execute.call_args.args[0]

        assert isinstance(statement, Select)

    def test_none_for_non_nullable_field_returns_validation_error(
        self,
    ) -> None:
        session = MagicMock()

        parameter_id = uuid7()

        repository = SqlAlchemyParameterMasterRepository(session)

        # item_value=None
        result = repository.update(
            ParameterMasterUpdate(
                id=parameter_id,
                item_value=None,
            ),
        )

        assert isinstance(result, Failure)

        error = result.failure()

        assert isinstance(error, ValidationError)

        # item_key=None
        result = repository.update(
            ParameterMasterUpdate(
                id=parameter_id,
                item_key=None,
            ),
        )

        assert isinstance(result, Failure)

        error = result.failure()

        assert isinstance(error, ValidationError)

        # ValidationErrorの場合、DBアクセスは発生しない
        session.execute.assert_not_called()

    def test_returns_database_error(self) -> None:
        session = MagicMock()

        parameter = ParameterMasterUpdate(
            id=uuid7(),
            item_key="test-key",
            item_value="test-value",
            item_fromdate=None,
        )

        session.execute.side_effect = SQLAlchemyError("database error")

        repository = SqlAlchemyParameterMasterRepository(session)

        result = repository.update(parameter)

        assert isinstance(result, Failure)

        error = result.failure()

        assert isinstance(error, DatabaseError)

        session.execute.assert_called_once()


class TestDeleteParameterMaster:
    def test_returns_deleted_parameter(self) -> None:
        session = MagicMock()

        parameter_id = uuid7()

        row_result = make_model(
            id=parameter_id,
            item_key="test-key",
            item_value="test-value",
            item_fromdate=None,
        )

        session.execute.return_value.scalar_one.return_value = row_result

        repository = SqlAlchemyParameterMasterRepository(session)

        result = repository.delete(parameter_id)

        assert isinstance(result, Success)
        assert result.unwrap() is None

        # DELETE Statementを取得
        session.execute.assert_called_once()
        statement = session.execute.call_args.args[0]

        # DELETEであることを確認
        assert isinstance(statement, Delete)

        # 対象テーブルを確認
        assert isinstance(statement.table, Table)
        assert statement.table.name == GyomuParamMaster.__tablename__

    def test_delete_returns_database_error(self) -> None:
        session = MagicMock()

        parameter_id = uuid7()

        session.execute.side_effect = SQLAlchemyError(
            "database error",
        )

        repository = SqlAlchemyParameterMasterRepository(session)

        result = repository.delete(parameter_id)

        assert isinstance(result, Failure)

        error = result.failure()

        assert isinstance(error, DatabaseError)

        session.execute.assert_called_once()
