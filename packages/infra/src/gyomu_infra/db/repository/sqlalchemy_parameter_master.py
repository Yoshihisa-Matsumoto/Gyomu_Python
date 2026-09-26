from uuid import UUID

from gyomu_schema.error.database import DatabaseError
from gyomu_schema.error.validation import ValidationError
from gyomu_schema.parameter.parameter_master import (
    ParameterMaster,
    ParameterMasterCreate,
    ParameterMasterUpdate,
)
from returns.result import Failure, Result, Success, safe
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from gyomu_infra.db.error.database import to_database_error
from gyomu_infra.db.mapper.parameter_master import (
    to_model_for_insert,
    to_model_for_update,
    to_schema,
)
from gyomu_infra.db.model.generated.models import GyomuParamMaster
from gyomu_infra.db.transaction.sqlalchemy_transaction_manager import (
    SqlAlchemyTransactionManager,
)
from gyomu_infra.db.transaction.transaction_manager import TransactionManager


class SqlAlchemyParameterMasterRepository:
    """SQLAlchemy implementation of the parameter master repository."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def transaction(self) -> TransactionManager:
        """Creates and returns a transaction manager for the session."""

        return SqlAlchemyTransactionManager(self._session, None)

    def find_by_item_key(
        self,
        item_key: str,
    ) -> Result[list[ParameterMaster], DatabaseError]:
        """Finds parameter master records matching the specified item key.

        Args:
            item_key (str):
        """
        return self._find_by_item_key(item_key).alt(
            to_database_error,
        )

    @safe(exceptions=(SQLAlchemyError,))
    def _find_by_item_key(
        self,
        item_key: str,
    ) -> list[ParameterMaster]:
        """Internal helper to query parameter master records by item key.

        Args:
            item_key (str):
        """
        statement = select(GyomuParamMaster).where(
            GyomuParamMaster.item_key == item_key
        )

        models = self._session.scalars(statement).all()

        return [to_schema(model) for model in models]

    def insert(
        self,
        parameter: ParameterMasterCreate,
    ) -> Result[ParameterMaster, DatabaseError]:
        """Inserts a new parameter master record.

        Args:
            parameter (ParameterMasterCreate):
        """
        return self._execute_insert(parameter).alt(
            to_database_error,
        )

    @safe(exceptions=(SQLAlchemyError,))
    def _execute_insert(
        self,
        parameter: ParameterMasterCreate,
    ) -> ParameterMaster:
        """Internal helper to execute parameter master record insertion.

        Args:
            parameter (ParameterMasterCreate):
        """
        model = to_model_for_insert(parameter)
        statement = insert(GyomuParamMaster).values(model).returning(GyomuParamMaster)

        result = self._session.execute(statement).scalar_one()

        return to_schema(result)

    def update(
        self,
        parameter: ParameterMasterUpdate,
    ) -> Result[ParameterMaster, DatabaseError | ValidationError]:
        """Updates an existing parameter master record.

        Args:
            parameter (ParameterMasterUpdate):
        """
        values_result = to_model_for_update(parameter)

        if isinstance(values_result, Failure):
            return values_result

        values = values_result.unwrap()
        if not values:
            return self._find_by_id(parameter.id).alt(
                to_database_error,
            )
        return self._execute_update(parameter.id, values).alt(
            to_database_error,
        )

    @safe(exceptions=(SQLAlchemyError,))
    def _execute_update(
        self,
        id: UUID,
        values: dict[str, object],
    ) -> ParameterMaster:
        """Internal helper to execute parameter master record update.

        Args:
            id (UUID):
            values (dict[str, object]):
        """
        statement = (
            update(GyomuParamMaster)
            .where(GyomuParamMaster.id == id)
            .values(values)
            .returning(GyomuParamMaster)
        )

        result = self._session.execute(statement).scalar_one()
        print(result)
        return to_schema(result)

    @safe(exceptions=(SQLAlchemyError,))
    def _find_by_id(
        self,
        id: UUID,
    ) -> ParameterMaster:
        """Internal helper to find a parameter master record by its unique ID.

        Args:
            id (UUID):
        """
        statement = select(GyomuParamMaster).where(GyomuParamMaster.id == id)

        result = self._session.execute(statement).scalar_one()

        return to_schema(result)

    def delete(
        self,
        id: UUID,
    ) -> Result[None, DatabaseError]:
        """Deletes a parameter master record by its unique ID.

        Args:
            id (UUID):
        """

        delete_result = self._execute_delete(id).alt(
            to_database_error,
        )
        if isinstance(delete_result, Failure):
            return delete_result
        return Success(None)

    @safe(exceptions=(SQLAlchemyError,))
    def _execute_delete(
        self,
        id: UUID,
    ) -> None:
        """Internal helper to execute parameter master record deletion.

        Args:
            id (UUID):
        """

        statement = delete(GyomuParamMaster).where(GyomuParamMaster.id == id)
        self._session.execute(statement)
