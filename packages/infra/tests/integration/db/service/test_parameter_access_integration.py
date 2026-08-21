import pytest
from gyomu_schema.parameter.parameter_master import ParameterMasterCreate
from returns.result import Success
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from gyomu_infra.db.model.generated.models import GyomuParamMaster
from gyomu_infra.db.repository.sqlalchemy_parameter_master import (
    SqlAlchemyParameterMasterRepository,
)
from gyomu_infra.gyomu.parameter.parameter_access import ParameterAccessImpl

TEST_ITEM_KEY = "##TEST-KEY###"


class TestParameterAccessIntegration:
    @pytest.fixture(autouse=True)
    def cleanup(self, db_engine):
        with Session(db_engine) as session:
            session.execute(
                delete(GyomuParamMaster).where(
                    GyomuParamMaster.item_key == TEST_ITEM_KEY
                )
            )
            session.commit()

        yield

        with Session(db_engine) as session:
            session.execute(
                delete(GyomuParamMaster).where(
                    GyomuParamMaster.item_key == TEST_ITEM_KEY
                )
            )
            session.commit()

    def test_get_value_returns_parameter(
        self,
        db_engine,
    ) -> None:
        with Session(db_engine) as session:
            repository = SqlAlchemyParameterMasterRepository(session)

            repository.insert(
                ParameterMasterCreate(item_key=TEST_ITEM_KEY, item_value="test-value")
            )
            session.commit()

            access = ParameterAccessImpl(repository)

            result = access.get_value(TEST_ITEM_KEY)

            assert result.unwrap() == "test-value"

    def test_set_value_inserts_parameter(
        self,
        db_engine,
    ) -> None:
        with Session(db_engine) as session:
            repository = SqlAlchemyParameterMasterRepository(session)
            access = ParameterAccessImpl(repository)

            result = access.set_value(TEST_ITEM_KEY, "test-value")

            assert result == Success(None)

        with Session(db_engine) as session:
            record = session.scalar(
                select(GyomuParamMaster).where(
                    GyomuParamMaster.item_key == TEST_ITEM_KEY,
                )
            )

            assert record is not None
            assert record.item_key == TEST_ITEM_KEY
            assert record.item_value == "test-value"
            assert record.item_fromdate is None

    def test_set_value_updates_parameter(
        self,
        db_engine,
    ) -> None:
        with Session(db_engine) as session:
            repository = SqlAlchemyParameterMasterRepository(session)

            insert_result = repository.insert(
                ParameterMasterCreate(
                    item_key=TEST_ITEM_KEY,
                    item_value="old-value",
                    item_fromdate=None,
                )
            )

            assert insert_result == Success(insert_result.unwrap())

            session.commit()

        with Session(db_engine) as session:
            repository = SqlAlchemyParameterMasterRepository(session)
            access = ParameterAccessImpl(repository)

            result = access.set_value(TEST_ITEM_KEY, "new-value")

            assert result == Success(None)

        with Session(db_engine) as session:
            record = session.scalar(
                select(GyomuParamMaster).where(
                    GyomuParamMaster.item_key == TEST_ITEM_KEY,
                )
            )

            assert record is not None
            assert record.item_value == "new-value"

    def test_set_value_deletes_parameter_when_value_is_empty(
        self,
        db_engine,
    ) -> None:
        with Session(db_engine) as session:
            repository = SqlAlchemyParameterMasterRepository(session)

            insert_result = repository.insert(
                ParameterMasterCreate(
                    item_key=TEST_ITEM_KEY,
                    item_value="test-value",
                    item_fromdate=None,
                )
            )

            assert isinstance(insert_result, Success)
            session.commit()

        with Session(db_engine) as session:
            repository = SqlAlchemyParameterMasterRepository(session)
            access = ParameterAccessImpl(repository)

            result = access.set_value(TEST_ITEM_KEY, "")

            assert result == Success(None)

        with Session(db_engine) as session:
            record = session.scalar(
                select(GyomuParamMaster).where(
                    GyomuParamMaster.item_key == TEST_ITEM_KEY,
                )
            )

            assert record is None

    def test_set_value_does_nothing_when_key_does_not_exist_and_value_is_empty(
        self,
        db_engine,
    ) -> None:
        with Session(db_engine) as session:
            repository = SqlAlchemyParameterMasterRepository(session)
            access = ParameterAccessImpl(repository)

            result = access.set_value(TEST_ITEM_KEY, "")

            assert result == Success(None)

        with Session(db_engine) as session:
            record = session.scalar(
                select(GyomuParamMaster).where(
                    GyomuParamMaster.item_key == TEST_ITEM_KEY,
                )
            )

            assert record is None

    def test_transaction_rolls_back_insert_on_failure(
        self,
        db_engine,
    ) -> None:
        with Session(db_engine) as session:
            repository = SqlAlchemyParameterMasterRepository(session)

            with pytest.raises(RuntimeError), repository.transaction():
                insert_result = repository.insert(
                    ParameterMasterCreate(
                        item_key=TEST_ITEM_KEY,
                        item_value="test-value",
                        item_fromdate=None,
                    )
                )

                assert isinstance(insert_result, Success)

                raise RuntimeError("intentional failure")

        with Session(db_engine) as session:
            record = session.scalar(
                select(GyomuParamMaster).where(
                    GyomuParamMaster.item_key == TEST_ITEM_KEY,
                )
            )

            assert record is None
