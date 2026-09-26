from collections.abc import Awaitable, Callable

from pydantic import BaseModel
from pydantic_ai import Tool

from gyomu_ai.tool.ai_tool import AiTool, ToolResult


def to_pydantic_ai_tool[InputT: BaseModel, OutputT, ConfigT: BaseModel](
    tool: AiTool[InputT, OutputT, ConfigT],
) -> Tool:
    """Converts an AiTool into a Pydantic AI Tool.

    Converts a generic AiTool instance into a Pydantic AI Tool instance.

    Args:
        tool (AiTool[InputT, OutputT, ConfigT]): The generic AI tool to convert.

    Returns:
        Tool: A Pydantic AI Tool instance.
    """
    result = Tool(
        description=tool.description,
        name=tool.name,
        function=call_from_pydantic_ai(tool),
    )
    return result


def call_from_pydantic_ai[InputT: BaseModel, OutputT, ConfigT: BaseModel](
    tool: AiTool[InputT, OutputT, ConfigT],
) -> Callable[[InputT], Awaitable[ToolResult[OutputT]]]:
    """Creates an execution wrapper for an AiTool compatible with Pydantic AI.

    Creates an asynchronous callable wrapper around an AiTool execution for use with
    Pydantic AI.

    Args:
        tool (AiTool[InputT, OutputT, ConfigT]): The generic AI tool to wrap.

    Returns:
        Callable[[InputT], Awaitable[ToolResult[OutputT]]]: An asynchronous callable
            that takes input and returns a ToolResult.
    """

    async def call_for_llm(input: InputT) -> ToolResult[OutputT]:
        # TODO: Resolve and inject ConfigT via gyomu-config.
        return await tool.execute(input, None)

    call_for_llm.__annotations__["input"] = tool.input_type
    call_for_llm.__doc__ = tool.execute.__doc__
    return call_for_llm
