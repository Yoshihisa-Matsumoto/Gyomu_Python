from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel


@dataclass(frozen=True)
class ToolSuccessResult[OutputT]:
    """Represents a successful tool execution result containing output data."""

    data: OutputT
    """The result data returned by the tool."""


@dataclass(frozen=True)
class PublicError:
    """Defines a public error response containing an error code, message, and
    retryability indicator.
    """

    code: str
    """The error code identifier."""

    message: str
    """The human-readable error description."""

    retryable: bool
    """Indicates whether the error is retryable."""


@dataclass(frozen=True)
class ToolFailureResult:
    """Represents a failed tool execution result containing error details."""

    error: PublicError
    """The public error details associated with the failure."""


type ToolResult[OutputT] = ToolSuccessResult[OutputT] | ToolFailureResult
"""Represents the result of a tool execution, which can be either a success or a
failure.
"""


@dataclass(frozen=True)
class AiToolConfig[ConfigT: BaseModel]:
    """Defines configuration settings and scope resolution mode for an AI tool."""

    config_type: type[ConfigT]
    """The Pydantic model class type used for configuration."""

    scope_resolution_mode: Literal["static", "runtime", "mixed"]
    """The mode used for resolving scopes (static, runtime, or mixed)."""


@dataclass(frozen=True)
class AiTool[InputT: BaseModel, OutputT, ConfigT: BaseModel]:
    """Defines an AI tool with metadata, input typing, configuration, and an
    execution handler.
    """

    name: str
    """The unique name of the tool."""

    description: str
    """A description of what the tool does."""

    input_type: type[InputT]
    """The Pydantic model class type defining the input arguments."""

    config: AiToolConfig[ConfigT] | None
    """The optional configuration definition for the tool."""

    execute: Callable[[InputT, ConfigT | None], Awaitable[ToolResult[OutputT]]]
    """The asynchronous function that executes the tool logic."""
