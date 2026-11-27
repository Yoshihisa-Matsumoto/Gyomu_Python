from pathlib import Path

from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.protocols.interaction import InteractionExecutor
from gyomu_schema.schemas.interaction.request import (
    InteractionRequest,
    InteractionSelectRequest,
    SelectionOption,
)
from gyomu_schema.schemas.interaction.result import InteractionCancelled
from returns.result import Failure, Result, Success


class SimpleConfirmationSelectionProvider:
    def create_selections(
        self, context: None
    ) -> Result[tuple[SelectionOption[bool], ...], GyomuError]:
        selections: list[SelectionOption[bool]] = []

        selections.append(SelectionOption[bool](label="Yes", value=True))
        selections.append(SelectionOption[bool](label="No", value=False))
        return Success(tuple(selections))


def _build_simple_confirm_selection_request(
    instructuion: str, initial_value: bool | None
) -> InteractionRequest[
    str,
    Path,
    None,
    bool,
]:
    return InteractionSelectRequest[None, bool](
        instruction=instructuion,
        context=None,
        selection_provider=SimpleConfirmationSelectionProvider(),
        initial_value=initial_value,
    )


def simple_confirm(
    instruction: str,
    interaction: InteractionExecutor[str, Path],
    initial_value: bool | None,
) -> Result[bool | None, GyomuError]:
    request = _build_simple_confirm_selection_request(
        instructuion=instruction, initial_value=initial_value
    )
    interaction_result = interaction.execute(request=request)
    if isinstance(interaction_result, Failure):
        return interaction_result
    reaction = interaction_result.unwrap()
    if isinstance(reaction, InteractionCancelled):
        return Success(None)

    return Success(reaction.value)
