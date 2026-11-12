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
    InteractionAccepted,
    InteractionCancelled,
    InteractionRejected,
    InteractionResult,
)
from returns.result import Failure, Result, Success


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

        while True:
            try:
                raw_input = self._input(f"{request.instruction}\n> ")
            except (EOFError, KeyboardInterrupt):
                return Success(InteractionCancelled())

            if raw_input == ":cancel":
                return Success(InteractionCancelled())

            if raw_input == ":reject":
                return Success(InteractionRejected())

            parsed = request.codec.parse(raw_input, request.context)

            if isinstance(parsed, Failure):
                error = parsed.failure()
                print(f"Invalid input: {error}", file=self._output)
                continue

            return Success(InteractionAccepted(parsed.unwrap()))
