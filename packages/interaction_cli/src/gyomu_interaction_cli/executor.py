import sys
from collections.abc import Callable
from typing import TextIO

from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.protocols.interaction import InteractionExecutor
from gyomu_schema.schemas.interaction.request import (
    InputMode,
    InteractionRequest,
)
from gyomu_schema.schemas.interaction.result import (
    InteractionResult,
)
from returns.result import Failure, Result

from gyomu_interaction_cli.direct import execute_direct_interaction


class CliInteractionExecutor(InteractionExecutor[str]):
    def __init__(
        self,
        *,
        input_func: Callable[[str], str] = input,
        output: TextIO | None = None,
    ) -> None:
        self._input = input_func
        self._output = sys.stdout if output is None else output

    def execute[ContextT, ValueT](
        self,
        request: InteractionRequest[str, ContextT, ValueT],
    ) -> Result[InteractionResult[ValueT], GyomuError]:
        if request.input_mode is not InputMode.DIRECT:
            return Failure(
                GyomuError(
                    "Unsupported interaction input mode.",
                    operation="Execution",
                    domain="Interaction CLI",
                    reason="invalid_input",
                    details={"input_mode": request.input_mode.value},
                )
            )

        return execute_direct_interaction(
            request=request, input_func=self._input, output=self._output
        )
