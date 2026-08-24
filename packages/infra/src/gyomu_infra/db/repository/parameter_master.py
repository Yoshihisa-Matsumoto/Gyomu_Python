from typing import Protocol
from uuid import UUID

from gyomu_schema.error.io import GyomuIOError
from gyomu_schema.error.validation import ValidationError
from gyomu_schema.parameter.parameter_master import (
    ParameterMaster,
    ParameterMasterCreate,
    ParameterMasterUpdate,
)
from returns.result import Result

from gyomu_infra.db.transaction.transaction_manager import TransactionManager


class ParameterMasterRepository(Protocol):
    def find_by_item_key(
        self,
        item_key: str,
    ) -> Result[list[ParameterMaster], GyomuIOError]: ...

    def insert(
        self,
        parameter: ParameterMasterCreate,
    ) -> Result[ParameterMaster, GyomuIOError]: ...

    def update(
        self,
        parameter: ParameterMasterUpdate,
    ) -> Result[ParameterMaster, GyomuIOError | ValidationError]: ...

    def delete(
        self,
        id: UUID,
    ) -> Result[None, GyomuIOError]: ...

    def transaction(self) -> TransactionManager: ...
