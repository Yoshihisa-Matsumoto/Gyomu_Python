from dataclasses import dataclass

from pydantic import BaseModel

from gyomu_ai.execution.context import AiExecutionContext
from gyomu_ai.model.ai_model import AiModelKey


@dataclass(frozen=True)
class GenerateTextParams:
    key: AiModelKey
    execution: AiExecutionContext
    tool: ToolConfig | None = None
    max_tokens: int | None = None


@dataclass(frozen=True)
class StreamTextParams:
    key: AiModelKey
    execution: AiExecutionContext
    tool: ToolConfig | None = None
    max_tokens: int | None = None


@dataclass(frozen=True)
class GenerateObjectParams[T: BaseModel]:
    key: AiModelKey
    output_type: type[T]
    tool: ToolConfig | None = None
    context: AiExecutionContext | None = None


@dataclass(frozen=True)
class EmbedParams[T]:
    execution: AiExecutionContext
    value: T


@dataclass(frozen=True)
class ToolLoopPolicyMaxSteps:
    max_steps: int


@dataclass(frozen=True)
class ToolLoopPolicyUntilToolCalled:
    tool_name: str


@dataclass(frozen=True)
class ToolLoopPolicyUntilFinished:
    pass


type ToolLoopPolicy = (
    ToolLoopPolicyMaxSteps | ToolLoopPolicyUntilToolCalled | ToolLoopPolicyUntilFinished
)


@dataclass(frozen=True)
class ToolConfig:
    tool_loop_policy: ToolLoopPolicy
