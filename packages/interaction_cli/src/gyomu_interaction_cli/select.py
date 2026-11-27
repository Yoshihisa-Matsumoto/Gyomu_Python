from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.schemas.interaction.request import (
    InteractionSelectRequest,
    SelectionOption,
)
from gyomu_schema.schemas.interaction.result import (
    InteractionAccepted,
    InteractionCancelled,
    InteractionResult,
)
from questionary import Choice, select
from returns.result import Failure, Result, Success


def _selection_to_choice[ValueT](
    selection: SelectionOption[ValueT], initial_value: ValueT | None
) -> Choice:
    return Choice(
        title=selection.label,
        value=selection.value,
        checked=bool(selection.value == initial_value and initial_value is not None),
    )


def execute_selection_interaction[ContextT, ValueT](
    request: InteractionSelectRequest[ContextT, ValueT],
) -> Result[InteractionResult[ValueT], GyomuError]:
    selection_result = request.selection_provider.create_selections(
        context=request.context
    )
    if isinstance(selection_result, Failure):
        return selection_result
    selections = selection_result.unwrap()
    if not selections:
        return Failure(
            GyomuError(
                message="fail to initialize selection items",
                operation="selection interaction",
                domain="interaction",
                reason="out_of_bounds",
            )
        )
    choices: list[Choice] = []
    for selection in selections:
        choices.append(
            _selection_to_choice(selection, initial_value=request.initial_value)
        )
    try:
        selected = select(message=request.instruction, choices=choices).ask()
        if selected is None:
            return Success(InteractionCancelled())

        return Success(InteractionAccepted(selected))
    except (EOFError, KeyboardInterrupt):
        return Success(InteractionCancelled())
