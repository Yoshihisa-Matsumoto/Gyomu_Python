from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Literal

from gyomu_schema.protocols.interaction import (
    DocumentCodec,
    DocumentTextProvider,
    SelectionProvider,
    ValueCodec,
)


class InputMode(StrEnum):
    DIRECT = "direct"
    DOCUMENT = "document"
    SELECT = "select"


@dataclass(frozen=True)
class InteractionBaseRequest[ContextT]:
    instruction: str
    context: ContextT


@dataclass(frozen=True)
class InteractionDirectRequest[RawInputT, ContextT, ValueT](
    InteractionBaseRequest[ContextT]
):
    codec: ValueCodec[RawInputT, ContextT, ValueT]

    input_mode: Literal[InputMode.DIRECT] = InputMode.DIRECT
    initial_value: ValueT | None = None


@dataclass(frozen=True)
class InteractionDocumentRequest[DocumentT, ContextT, ValueT](
    InteractionBaseRequest[ContextT]
):
    codec: DocumentCodec[DocumentT, ContextT, ValueT]
    text_provider: DocumentTextProvider[ContextT]
    input_mode: Literal[InputMode.DOCUMENT] = InputMode.DOCUMENT
    initial_value: ValueT | None = None
    temporary_directory: Path | None = None
    temporary_file_extension: str | None = None


@dataclass(frozen=True)
class SelectionOption[ValueT]:
    label: str
    value: ValueT


@dataclass(frozen=True)
class InteractionSelectRequest[ContextT, ValueT](InteractionBaseRequest[ContextT]):
    selection_provider: SelectionProvider[ContextT, ValueT]
    input_mode: Literal[InputMode.SELECT] = InputMode.SELECT
    initial_value: ValueT | None = None


type InteractionRequest[DirectRawInputT, DocumentT, ContextT, ValueT] = (
    InteractionDirectRequest[DirectRawInputT, ContextT, ValueT]
    | InteractionDocumentRequest[DocumentT, ContextT, ValueT]
    | InteractionSelectRequest[ContextT, ValueT]
)
