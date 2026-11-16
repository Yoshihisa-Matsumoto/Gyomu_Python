from collections.abc import Callable
from typing import TextIO

from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.schemas.interaction.request import (
    InteractionDirectRequest,
)
from gyomu_schema.schemas.interaction.result import (
    InteractionAccepted,
    InteractionCancelled,
    InteractionResult,
)
from returns.result import Failure, Result, Success

from gyomu_interaction_cli.confirm import confirm_or_cancel


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

        parsed = request.codec.parse(raw_input, request.context)

        if isinstance(parsed, Failure):
            error = parsed.failure()
            print(f"Invalid input: {error}", file=output)
            continue

        while True:
            if not confirm_or_cancel(input_func=input_func, output=output):
                return Success(InteractionCancelled())

            return Success(InteractionAccepted(parsed.unwrap()))
