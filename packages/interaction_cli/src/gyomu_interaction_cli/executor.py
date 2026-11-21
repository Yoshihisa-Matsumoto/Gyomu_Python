from pathlib import Path

from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.protocols.interaction import InteractionExecutor
from gyomu_schema.schemas.interaction.request import (
    InputMode,
    InteractionRequest,
)
from gyomu_schema.schemas.interaction.result import (
    InteractionResult,
)
from returns.result import Result

from gyomu_interaction_cli.direct import execute_direct_interaction
from gyomu_interaction_cli.document import execute_document_interaction
from gyomu_interaction_cli.select import execute_selection_interaction


class CliInteractionExecutor(InteractionExecutor[str, Path]):
    def execute[ContextT, ValueT](
        self,
        request: InteractionRequest[str, Path, ContextT, ValueT],
    ) -> Result[InteractionResult[ValueT], GyomuError]:
        if request.input_mode == InputMode.DIRECT:
            return execute_direct_interaction(request=request)
        if request.input_mode == InputMode.DOCUMENT:
            return execute_document_interaction(request=request)
        else:
            return execute_selection_interaction(request=request)
