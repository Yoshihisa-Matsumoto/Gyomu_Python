from collections.abc import Awaitable, Callable

from gyomu_ai.tool.ai_tool import AiTool, ToolResult
from pydantic import BaseModel
from pydantic_ai import Tool


def to_pydantic_ai_tool[InputT: BaseModel, OutputT, ConfigT: BaseModel](
    tool: AiTool[InputT, OutputT, ConfigT],
) -> Tool:
    result = Tool(
        description=tool.description,
        name=tool.name,
        function=call_from_pydantic_ai(tool),
    )
    return result


def call_from_pydantic_ai[InputT: BaseModel, OutputT, ConfigT: BaseModel](
    tool: AiTool[InputT, OutputT, ConfigT],
) -> Callable[[InputT], Awaitable[ToolResult[OutputT]]]:

    async def call_for_llm(input: InputT) -> ToolResult[OutputT]:
        # TODO: Resolve and inject ConfigT via gyomu-config.
        return await tool.execute(input, None)

    call_for_llm.__annotations__["input"] = tool.input_type
    call_for_llm.__doc__ = tool.execute.__doc__
    return call_for_llm
