from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from returns.result import Result

from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.error.validation import ValidationError

if TYPE_CHECKING:
    from gyomu_schema.schemas.interaction.request import InteractionRequest
    from gyomu_schema.schemas.interaction.result import InteractionResult


class ValueCodec[RawInputT, ContextT, ValueT](Protocol):
    def parse(
        self,
        raw_input: RawInputT,
        context: ContextT,
    ) -> Result[ValueT, ValidationError]: ...


class InteractionExecutor[RawInputT](Protocol):
    def execute[ContextT, ValueT](
        self,
        request: InteractionRequest[RawInputT, ContextT, ValueT],
    ) -> Result[InteractionResult[ValueT], GyomuError]: ...
