from typing import Any

from gyomu_ai.execution.parameter import (
    ToolConfig,
    ToolLoopPolicyMaxSteps,
    ToolLoopPolicyUntilFinished,
)
from gyomu_ai.provider.pydantic_ai.create_agent import (
    create_pydantic_ai_agent,
    create_pydantic_ai_agent_for_object,
)
from gyomu_ai.tool.ai_tool import (
    AiTool,
    ToolSuccessResult,
)
from pydantic import BaseModel
from pydantic_ai import Agent, UsageLimits
from pydantic_ai.models.test import TestModel


class SearchFileInput(BaseModel):
    path: str


class SearchFileConfig(BaseModel):
    allowed_root: str


class SearchFileOutput(BaseModel):
    files: list[str]


class TestCreatePydanticAiAgent:
    def _create_tool(
        self,
    ) -> AiTool[
        SearchFileInput,
        Any,
        SearchFileConfig,
    ]:
        async def execute(
            input: SearchFileInput,
            config: SearchFileConfig | None,
        ) -> ToolSuccessResult[Any]:
            return ToolSuccessResult(data=input.path)

        return AiTool(
            name="search_file",
            description="Search files.",
            input_type=SearchFileInput,
            config=None,
            execute=execute,
        )

    def test_creates_agent_without_tools(
        self,
    ) -> None:
        model = TestModel()

        agent, usage_limits = create_pydantic_ai_agent(
            model,
            None,
        )

        assert isinstance(agent, Agent)
        assert usage_limits is None

    def test_creates_agent_with_tool(
        self,
    ) -> None:
        model = TestModel()
        tool = self._create_tool()

        config = ToolConfig(
            tool_loop_policy=ToolLoopPolicyMaxSteps(max_steps=3),
            tools=[tool],
        )

        agent, usage_limits = create_pydantic_ai_agent(
            model,
            config,
        )

        assert isinstance(agent, Agent)
        assert usage_limits is not None

        assert usage_limits.tool_calls_limit == 3

        assert len(agent._function_toolset.tools) == 1

        registered_tool = agent._function_toolset.tools["search_file"]

        assert registered_tool.name == "search_file"
        assert registered_tool.description == "Search files."

    def test_maps_max_steps_to_usage_limits(
        self,
    ) -> None:
        model = TestModel()
        tool = self._create_tool()

        config = ToolConfig(
            tool_loop_policy=ToolLoopPolicyMaxSteps(max_steps=5),
            tools=[tool],
        )

        _, usage_limits = create_pydantic_ai_agent(
            model,
            config,
        )

        assert isinstance(usage_limits, UsageLimits)
        assert usage_limits.tool_calls_limit == 5

    def test_returns_no_usage_limits_when_policy_is_until_finished(
        self,
    ) -> None:
        model = TestModel()
        tool = self._create_tool()

        config = ToolConfig(
            tool_loop_policy=ToolLoopPolicyUntilFinished(),
            tools=[tool],
        )

        _, usage_limits = create_pydantic_ai_agent(
            model,
            config,
        )

        assert usage_limits is None

    def test_creates_object_agent_without_tools(
        self,
    ) -> None:
        model = TestModel()

        agent, usage_limits = create_pydantic_ai_agent_for_object(
            model,
            SearchFileOutput,
            None,
        )

        assert isinstance(agent, Agent)
        assert usage_limits is None

        assert agent.output_type == SearchFileOutput

    def test_creates_object_agent_with_tool(
        self,
    ) -> None:
        model = TestModel()
        tool = self._create_tool()

        config = ToolConfig(
            tool_loop_policy=ToolLoopPolicyMaxSteps(max_steps=3),
            tools=[tool],
        )

        agent, usage_limits = create_pydantic_ai_agent_for_object(
            model,
            SearchFileOutput,
            config,
        )

        assert isinstance(agent, Agent)
        assert usage_limits is not None

        assert usage_limits.tool_calls_limit == 3

        assert agent.output_type == SearchFileOutput

        assert len(agent._function_toolset.tools) == 1

        registered_tool = agent._function_toolset.tools["search_file"]

        assert registered_tool.name == "search_file"
        assert registered_tool.description == "Search files."

    def test_maps_max_steps_to_usage_limits_for_object_agent(
        self,
    ) -> None:
        model = TestModel()
        tool = self._create_tool()

        config = ToolConfig(
            tool_loop_policy=ToolLoopPolicyMaxSteps(max_steps=5),
            tools=[tool],
        )

        _, usage_limits = create_pydantic_ai_agent_for_object(
            model,
            SearchFileOutput,
            config,
        )

        assert isinstance(usage_limits, UsageLimits)
        assert usage_limits.tool_calls_limit == 5

    def test_returns_no_usage_limits_when_policy_is_until_finished_for_object_agent(
        self,
    ) -> None:
        model = TestModel()
        tool = self._create_tool()

        config = ToolConfig(
            tool_loop_policy=ToolLoopPolicyUntilFinished(),
            tools=[tool],
        )

        _, usage_limits = create_pydantic_ai_agent_for_object(
            model,
            SearchFileOutput,
            config,
        )

        assert usage_limits is None
