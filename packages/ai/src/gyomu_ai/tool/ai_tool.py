from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel


@dataclass(frozen=True)
class ToolSuccessResult[OutputT]:
    data: OutputT


@dataclass(frozen=True)
class PublicError:
    code: str
    message: str
    retryable: bool


@dataclass(frozen=True)
class ToolFailureResult:
    error: PublicError


type ToolResult[OutputT] = ToolSuccessResult[OutputT] | ToolFailureResult


@dataclass(frozen=True)
class AiToolConfig[ConfigT: BaseModel]:
    config_type: type[ConfigT]
    scope_resolution_mode: Literal["static", "runtime", "mixed"]


@dataclass(frozen=True)
class AiTool[InputT: BaseModel, OutputT, ConfigT: BaseModel]:
    name: str
    description: str
    input_type: type[InputT]
    config: AiToolConfig[ConfigT] | None
    execute: Callable[[InputT, ConfigT | None], Awaitable[ToolResult[OutputT]]]
