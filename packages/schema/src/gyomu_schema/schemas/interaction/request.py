from dataclasses import dataclass
from enum import StrEnum
from typing import Literal

from gyomu_schema.protocols.interaction import DocumentTextProvider, ValueCodec


class InputMode(StrEnum):
    DIRECT = "direct"
    DOCUMENT = "document"


@dataclass(frozen=True)
class InteractionBaseRequest[RawInputT, ContextT, ValueT]:
    instruction: str
    context: ContextT
    codec: ValueCodec[RawInputT, ContextT, ValueT]
    input_mode: InputMode
    initial_value: ValueT | None


@dataclass(frozen=True)
class InteractionDirectRequest[RawInputT, ContextT, ValueT](
    InteractionBaseRequest[RawInputT, ContextT, ValueT]
):
    input_mode: Literal[InputMode.DIRECT] = InputMode.DIRECT
    initial_value: ValueT | None = None


@dataclass(frozen=True)
class InteractionDocumentRequest[RawInputT, ContextT, ValueT](
    InteractionBaseRequest[RawInputT, ContextT, ValueT]
):
    text_provider: DocumentTextProvider[ContextT]
    input_mode: Literal[InputMode.DOCUMENT] = InputMode.DOCUMENT
    initial_value: ValueT | None = None


type InteractionRequest[RawInputT, ContextT, ValueT] = (
    InteractionDirectRequest[RawInputT, ContextT, ValueT]
    | InteractionDocumentRequest[RawInputT, ContextT, ValueT]
)
