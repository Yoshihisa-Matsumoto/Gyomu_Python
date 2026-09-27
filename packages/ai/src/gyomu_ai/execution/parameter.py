from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from pydantic import BaseModel

from gyomu_ai.execution.context import AiExecutionContext
from gyomu_ai.model.ai_model import AiModelKey
from gyomu_ai.tool.ai_tool import AiTool


@dataclass(frozen=True)
class ToolLoopPolicyMaxSteps:
    """Policy to limit tool execution loops by maximum step count.

    Policy to limit tool execution loops by maximum step count.
    """

    max_steps: int
    """Maximum number of steps allowed in the tool loop.

    Maximum number of steps allowed in the tool loop.
    """


@dataclass(frozen=True)
class ToolLoopPolicyUntilToolCalled:
    """Policy to run tool execution until a specific tool is called.

    Policy to run tool execution until a specific tool is called.
    """

    tool_name: str
    """Name of the tool that stops the loop when called.

    Name of the tool that stops the loop when called.
    """


@dataclass(frozen=True)
class ToolLoopPolicyUntilFinished:
    """Policy to run tool execution until finished.

    Policy to run tool execution until finished.
    """

    pass


type ToolLoopPolicy = (
    ToolLoopPolicyMaxSteps | ToolLoopPolicyUntilToolCalled | ToolLoopPolicyUntilFinished
)
"""Type union representing different policies for tool execution loops.

Type union representing different policies for tool execution loops.
"""


@dataclass(frozen=True)
class ToolConfig:
    """Configuration for AI tools and their execution loop behavior.

    Configuration for AI tools and their execution loop behavior.
    """

    tool_loop_policy: ToolLoopPolicy
    """Policy governing the tool execution loop.

    Policy governing the tool execution loop.
    """
    tools: Sequence[AiTool[Any, Any, Any]]
    """Sequence of available AI tools.

    Sequence of available AI tools.
    """


@dataclass(frozen=True)
class GenerateTextParams:
    """Parameters for generating text using an AI model.

    Parameters for generating text using an AI model.
    """

    key: AiModelKey
    """Model key identifying the AI model to use.

    Model key identifying the AI model to use.
    """
    execution: AiExecutionContext | None = None
    """Execution context for the AI call.

    Execution context for the AI call.
    """
    tool: ToolConfig | None = None
    """Tool configuration for tool-enabled generation.

    Tool configuration for tool-enabled generation.
    """


@dataclass(frozen=True)
class StreamTextParams:
    """Parameters for streaming text generation from an AI model.

    Parameters for streaming text generation from an AI model.
    """

    key: AiModelKey
    """Model key identifying the AI model to use.

    Model key identifying the AI model to use.
    """
    execution: AiExecutionContext | None = None
    """Execution context for the AI call.

    Execution context for the AI call.
    """
    tool: ToolConfig | None = None
    """Tool configuration for tool-enabled generation.

    Tool configuration for tool-enabled generation.
    """


@dataclass(frozen=True)
class GenerateObjectParams[T: BaseModel]:
    """Parameters for generating structured objects from an AI model.

    Parameters for generating structured objects from an AI model.
    """

    key: AiModelKey
    """Model key identifying the AI model to use.

    Model key identifying the AI model to use.
    """
    output_type: type[T]
    """Target output model type for structured generation.

    Target output model type for structured generation.
    """
    execution: AiExecutionContext | None = None
    """Execution context for the AI call.

    Execution context for the AI call.
    """
    tool: ToolConfig | None = None
    """Tool configuration for tool-enabled generation.

    Tool configuration for tool-enabled generation.
    """


class AiEmbeddingMode(StrEnum):
    """Mode of embedding for AI models (query or document).

    Mode of embedding for AI models (query or document).
    """

    QUERY = "query"
    """Query embedding mode.

    Query embedding mode.
    """
    DOCUMENT = "document"
    """Document embedding mode.

    Document embedding mode.
    """


@dataclass(frozen=True)
class EmbedParams[T]:
    """Parameters for generating vector embeddings.

    Parameters for generating vector embeddings.
    """

    value: T
    """Value or content to embed.

    Value or content to embed.
    """
    mode: AiEmbeddingMode
    """Embedding mode to apply.

    Embedding mode to apply.
    """
    execution: AiExecutionContext | None = None
    """Execution context for the embedding call.

    Execution context for the embedding call.
    """
