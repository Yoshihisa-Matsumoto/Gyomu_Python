from gyomu_ai.execution.parameter import (
    ToolConfig,
    ToolLoopPolicy,
    ToolLoopPolicyMaxSteps,
)
from gyomu_ai.provider.pydantic_ai.map_tool import to_pydantic_ai_tool
from pydantic import BaseModel
from pydantic_ai import Agent, UsageLimits
from pydantic_ai.models import Model


def create_pydantic_ai_agent_for_object[T: BaseModel](
    model: Model,
    output_type: type[T],
    tool: ToolConfig | None = None,
) -> tuple[Agent[object, T], UsageLimits | None]:
    if tool is None:
        return Agent(model=model, output_type=output_type), None
    else:
        tools = [to_pydantic_ai_tool(t) for t in tool.tools]
        return Agent(
            model=model, output_type=output_type, tools=tools
        ), _map_usage_limits(tool.tool_loop_policy)


def create_pydantic_ai_agent(
    model: Model, tool: ToolConfig | None = None
) -> tuple[Agent, UsageLimits | None]:
    if tool is None:
        return Agent(model=model), None
    else:
        tools = [to_pydantic_ai_tool(t) for t in tool.tools]
        return Agent(model=model, tools=tools), _map_usage_limits(tool.tool_loop_policy)


def _map_usage_limits(tool_loop_policy: ToolLoopPolicy | None) -> UsageLimits | None:
    if tool_loop_policy is None:
        return None
    if isinstance(tool_loop_policy, ToolLoopPolicyMaxSteps):
        return UsageLimits(tool_calls_limit=tool_loop_policy.max_steps)
    return None
