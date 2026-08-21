from datetime import date
from decimal import Decimal
from typing import Protocol

from gyomu_schema.error.io import GyomuIOError
from gyomu_schema.error.validation import ValidationError
from gyomu_schema.gyomu.user import User
from returns.result import Result


class ParameterAccess(Protocol):
    def _get_item_key(self, key: str, user: User | None = None) -> str: ...

    def get_value(
        self,
        key: str,
        user: User | None = None,
        target_date: date | None = None,
    ) -> Result[str, GyomuIOError]:
        """
        Gyomu Context:
            ParameterAccess is a service for retrieving application-level
            parameter values.

            target_date is not a database search date. It represents the
            reference date used to determine which parameter value should
            be effective at that point in time.

            ParameterMaster.item_fromdate does not represent the date on
            which the database record was created. It represents the date
            from which the parameter value becomes effective.

            When target_date is specified, the parameter value with the
            latest item_fromdate that is not later than target_date is
            considered the effective value.

            A record without item_fromdate is treated as the default value.

            When target_date is None, date-based parameter resolution is
            not performed. The first ParameterMaster record returned by
            the repository is returned as the parameter value.

            Omitting target_date means that the caller knows that the
            parameter is not dependent on a date.
        """
        ...

    def get_bool_value(
        self,
        key: str,
        user: User | None = None,
        target_date: date | None = None,
    ) -> Result[bool, GyomuIOError]: ...

    def get_int_value(
        self,
        key: str,
        user: User | None = None,
        target_date: date | None = None,
    ) -> Result[int, GyomuIOError | ValidationError]: ...

    def get_decimal_value(
        self,
        key: str,
        user: User | None = None,
        target_date: date | None = None,
    ) -> Result[Decimal, GyomuIOError | ValidationError]: ...

    def key_exists(
        self, key: str, user: User | None = None
    ) -> Result[bool, GyomuIOError]: ...

    def set_value(
        self, key: str, value: str, user: User | None = None
    ) -> Result[None, GyomuIOError | ValidationError]:
        """
        Gyomu Context:
            set_value manages the current value of a parameter.

            This operation does not manage date-based parameter history.
            Parameters set through this service are always date-independent
            and therefore have no item_fromdate.

            Date-based parameter history, including creating or splitting
            effective-date ranges, is outside the responsibility of
            ParameterAccess and must be managed through another data access
            mechanism.

            If the parameter exists, its current value is updated.
            If the parameter does not exist, a new parameter is created.
            If value is empty, an existing parameter is deleted. If the
            parameter does not exist, no operation is performed.
        """
        ...
