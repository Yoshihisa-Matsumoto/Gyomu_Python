from dataclasses import dataclass
from enum import StrEnum

from gyomu_schema.protocols.interaction import ValueCodec


class InputMode(StrEnum):
    DIRECT = "direct"
    DOCUMENT = "document"


@dataclass(frozen=True)
class InteractionRequest[RawInputT, ContextT, ValueT]:
    instruction: str
    input_mode: InputMode
    context: ContextT
    codec: ValueCodec[RawInputT, ContextT, ValueT]
    initial_value: ValueT | None = None
