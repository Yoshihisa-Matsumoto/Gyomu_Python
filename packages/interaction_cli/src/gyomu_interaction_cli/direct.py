from collections.abc import Callable
from typing import TextIO

from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.schemas.interaction.request import (
    InteractionDirectRequest,
)
from gyomu_schema.schemas.interaction.result import (
    InteractionAccepted,
    InteractionCancelled,
    InteractionRejected,
    InteractionResult,
)
from returns.result import Failure, Result, Success


def execute_direct_interaction[ContextT, ValueT](
    request: InteractionDirectRequest[str, ContextT, ValueT],
    *,
    input_func: Callable[[str], str],
    output: TextIO,
) -> Result[InteractionResult[ValueT], GyomuError]:

    while True:
        try:
            raw_input = input_func(f"{request.instruction}\n> ")
        except (EOFError, KeyboardInterrupt):
            return Success(InteractionCancelled())

        if raw_input == ":cancel":
            return Success(InteractionCancelled())

        if raw_input == ":reject":
            return Success(InteractionRejected())

        parsed = request.codec.parse(raw_input, request.context)

        if isinstance(parsed, Failure):
            error = parsed.failure()
            print(f"Invalid input: {error}", file=output)
            continue

        return Success(InteractionAccepted(parsed.unwrap()))
