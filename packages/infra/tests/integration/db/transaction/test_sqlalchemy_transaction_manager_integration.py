from uuid import uuid4, uuid7

import pytest
from gyomu_schema.parameter.parameter_master import ParameterMasterCreate
from returns.result import Success
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from gyomu_infra.db.model.generated.models import GyomuParamMaster
from gyomu_infra.db.repository.sqlalchemy_parameter_master import (
    SqlAlchemyParameterMasterRepository,
)
from gyomu_infra.db.transaction.sqlalchemy_transaction_manager import (
    SqlAlchemyTransactionManager,
)

TEST_ITEM_KEY = "##TEST-KEY###"

pytestmark = pytest.mark.integration


@pytest.fixture(autouse=True)
def cleanup_parameter(db_engine: Engine):
    with Session(db_engine) as session:
        session.query(GyomuParamMaster).filter(
            GyomuParamMaster.item_key == TEST_ITEM_KEY
        ).delete()
        session.commit()

    yield

    with Session(db_engine) as session:
        session.query(GyomuParamMaster).filter(
            GyomuParamMaster.item_key == TEST_ITEM_KEY
        ).delete()
        session.commit()


class TestSqlAlchemyTransactionManager:
    def test_commit(self, db_engine: Engine) -> None:

        with Session(db_engine) as session:
            repository = SqlAlchemyParameterMasterRepository(session)
            transaction = SqlAlchemyTransactionManager(session, None)

            with transaction:
                result = repository.insert(
                    ParameterMasterCreate(
                        item_key=TEST_ITEM_KEY,
                        item_value="commit-test",
                        item_fromdate=None,
                    )
                )

                assert isinstance(result, Success)
        parameter_id = result.unwrap().id
        with Session(db_engine) as session:
            result = session.execute(
                select(GyomuParamMaster).where(
                    GyomuParamMaster.id == parameter_id,
                )
            ).scalar_one_or_none()

            assert result is not None
            assert result.item_key == TEST_ITEM_KEY
            assert result.item_value == "commit-test"

    def test_rollback_on_exception(self, db_engine: Engine) -> None:

        with pytest.raises(RuntimeError), Session(db_engine) as session:
            repository = SqlAlchemyParameterMasterRepository(session)
            transaction = SqlAlchemyTransactionManager(session, None)

            with transaction:
                result = repository.insert(
                    ParameterMasterCreate(
                        item_key=TEST_ITEM_KEY,
                        item_value="rollback-test",
                        item_fromdate=None,
                    )
                )

                assert isinstance(result, Success)

                raise RuntimeError("rollback test")

        with Session(db_engine) as session:
            result = session.execute(
                select(GyomuParamMaster).where(
                    GyomuParamMaster.id == uuid7(),
                )
            ).scalar_one_or_none()

            assert result is None

    def test_explicit_rollback(self, db_engine: Engine) -> None:
        parameter_id = uuid4()

        with Session(db_engine) as session:
            repository = SqlAlchemyParameterMasterRepository(session)
            transaction = SqlAlchemyTransactionManager(session, None)

            with transaction:
                result = repository.insert(
                    ParameterMasterCreate(
                        item_key=TEST_ITEM_KEY,
                        item_value="explicit-rollback-test",
                        item_fromdate=None,
                    )
                )

                assert isinstance(result, Success)

                rollback_result = transaction.rollback()

                assert isinstance(rollback_result, Success)

        with Session(db_engine) as session:
            result = session.execute(
                select(GyomuParamMaster).where(
                    GyomuParamMaster.id == parameter_id,
                )
            ).scalar_one_or_none()

            assert result is None
