import decimal
from datetime import date
from decimal import Decimal

from gyomu_schema.error.database import DatabaseError
from gyomu_schema.error.io import GyomuIOError
from gyomu_schema.error.validation import ValidationError
from gyomu_schema.gyomu.parameter.parameter_access import ParameterAccess
from gyomu_schema.gyomu.user import User
from gyomu_schema.parameter.parameter_master import (
    ParameterMasterCreate,
    ParameterMasterUpdate,
)
from returns.result import Failure, Result, Success
from sqlalchemy.orm import Session

from gyomu_infra.db.repository.parameter_master import ParameterMasterRepository
from gyomu_infra.db.repository.sqlalchemy_parameter_master import (
    SqlAlchemyParameterMasterRepository,
)


class ParameterAccessImpl:
    def __init__(self, repository: ParameterMasterRepository) -> None:
        self.repository = repository

    def _get_item_key(self, key: str, user: User | None = None) -> str:
        if user is not None:
            key = user.user_id + "_" + key
        return key

    def get_value(
        self,
        key: str,
        user: User | None = None,
        target_date: date | None = None,
    ) -> Result[str, GyomuIOError]:
        item_key = self._get_item_key(key, user)
        load_data_result = self.repository.find_by_item_key(item_key)

        if isinstance(load_data_result, Failure):
            return load_data_result

        load_data = load_data_result.unwrap()

        if not load_data:
            return Failure(
                DatabaseError(f"Can not retrieve parameter value for key: {item_key}")
            )

        if target_date is None:
            return Success(load_data[0].item_value)

        default_values = [
            parameter
            for parameter in load_data
            if parameter.item_fromdate is None or not parameter.item_fromdate.strip()
        ]

        if len(default_values) > 1:
            return Failure(
                DatabaseError(
                    "Multiple default values found. "
                    "Please ensure there is only one default value "
                    "without item_fromdate."
                )
            )

        if not default_values:
            return Failure(
                DatabaseError(
                    f"No default value found for key: {item_key}, "
                    f"target_date: {target_date:%Y-%m-%d}"
                )
            )

        item_value = default_values[0].item_value
        target_ymd = target_date.strftime("%Y-%m-%d")

        dated_values = [
            parameter
            for parameter in load_data
            if parameter.item_fromdate is not None and parameter.item_fromdate.strip()
        ]

        for parameter in sorted(
            dated_values,
            key=lambda parameter: parameter.item_fromdate or "",
        ):
            assert parameter.item_fromdate is not None

            if target_ymd == parameter.item_fromdate:
                return Success(parameter.item_value)

            if target_ymd < parameter.item_fromdate:
                break

            item_value = parameter.item_value

        return Success(item_value)

    def get_bool_value(
        self,
        key: str,
        user: User | None = None,
        target_date: date | None = None,
    ) -> Result[bool, GyomuIOError]:
        return self.get_value(key, user, target_date).map(
            lambda value: value.lower() == "true"
        )

    def get_int_value(
        self,
        key: str,
        user: User | None = None,
        target_date: date | None = None,
    ) -> Result[int, GyomuIOError | ValidationError]:
        result = self.get_value(key, user, target_date)

        if isinstance(result, Failure):
            return result
        return _parse_int(result.unwrap())

    def get_decimal_value(
        self,
        key: str,
        user: User | None = None,
        target_date: date | None = None,
    ) -> Result[Decimal, GyomuIOError | ValidationError]:
        result = self.get_value(key, user, target_date)

        if isinstance(result, Failure):
            return result
        return _parse_decimal(result.unwrap())

    def key_exists(
        self, key: str, user: User | None = None
    ) -> Result[bool, GyomuIOError]:
        item_key = self._get_item_key(key, user)
        record_result = self.repository.find_by_item_key(item_key)
        if isinstance(record_result, Failure):
            return record_result
        record = record_result.unwrap()
        return Success(len(record) > 0)

    def set_value(
        self, key: str, value: str, user: User | None = None
    ) -> Result[None, GyomuIOError | ValidationError]:
        item_key = self._get_item_key(key, user)

        with self.repository.transaction() as trn:
            records_result = self.repository.find_by_item_key(item_key)

            if isinstance(records_result, Failure):
                trn.rollback()
                return records_result

            records = records_result.unwrap()

            if records:
                target_record = records[0]

                if value == "":
                    delete_result = self.repository.delete(target_record.id)

                    if isinstance(delete_result, Failure):
                        trn.rollback()
                        return delete_result

                else:
                    update_result = self.repository.update(
                        ParameterMasterUpdate(
                            id=target_record.id,
                            item_value=value,
                        )
                    )

                    if isinstance(update_result, Failure):
                        trn.rollback()
                        return update_result

            elif value != "":
                insert_result = self.repository.insert(
                    ParameterMasterCreate(
                        item_key=item_key,
                        item_value=value,
                        item_fromdate=None,
                    )
                )

                if isinstance(insert_result, Failure):
                    trn.rollback()
                    return insert_result

            return Success(None)


def _parse_int(value: str) -> Result[int, ValidationError]:
    try:
        return Success(int(value))
    except ValueError:
        return Failure(
            ValidationError(message=f"Invalid integer parameter value: {value}")
        )


def _parse_decimal(value: str) -> Result[Decimal, ValidationError]:
    try:
        return Success(Decimal(value))
    except decimal.InvalidOperation:
        return Failure(
            ValidationError(message=f"Invalid decimal parameter value: {value}")
        )


def create_parameter_access(
    session: Session,
) -> ParameterAccess:
    repository = SqlAlchemyParameterMasterRepository(session)
    return ParameterAccessImpl(repository)
