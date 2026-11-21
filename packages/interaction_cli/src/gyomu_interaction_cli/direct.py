from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.schemas.interaction.request import (
    InteractionDirectRequest,
)
from gyomu_schema.schemas.interaction.result import (
    InteractionAccepted,
    InteractionCancelled,
    InteractionResult,
)
from questionary import text
from returns.result import Failure, Result, Success

from gyomu_interaction_cli.confirm import confirm_or_cancel


def execute_direct_interaction[ContextT, ValueT](
    request: InteractionDirectRequest[str, ContextT, ValueT],
) -> Result[InteractionResult[ValueT], GyomuError]:
    while True:
        raw_input = text(
            f"{request.instruction}\n>",
        ).ask()

        if raw_input is None:
            return Success(InteractionCancelled())

        parsed = request.codec.parse(raw_input, request.context)

        if isinstance(parsed, Failure):
            error = parsed.failure()
            print(f"Invalid input: {error}")
            continue

        if not confirm_or_cancel():
            return Success(InteractionCancelled())

        return Success(InteractionAccepted(parsed.unwrap()))
