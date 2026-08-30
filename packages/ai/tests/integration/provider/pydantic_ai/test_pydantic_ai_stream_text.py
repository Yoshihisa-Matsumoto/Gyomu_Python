import pytest
from gyomu_ai.execution.context import AiExecutionContext
from gyomu_ai.execution.parameter import (
    StreamTextParams,
    ToolConfig,
    ToolLoopPolicyMaxSteps,
)
from gyomu_ai.model.ai_model import AiModelKey
from gyomu_ai.provider.pydantic_ai.ai_model import PydanticAiModelRegistry
from gyomu_ai.provider.pydantic_ai.execution import PydanticAiModelExecution
from gyomu_ai.tool.ai_tool import (
    AiTool,
    PublicError,
    ToolFailureResult,
    ToolResult,
    ToolSuccessResult,
)
from gyomu_schema.conversation.conversation import ConversationSchema
from gyomu_schema.conversation.message import MessageSchema
from pydantic import BaseModel
from returns.result import Success

pytestmark = pytest.mark.integration


class GetValueInput(BaseModel):
    key: str


class GetValueConfig(BaseModel):
    allowed_key: str


@pytest.mark.integration
@pytest.mark.asyncio
async def test_stream_text(registry: PydanticAiModelRegistry) -> None:

    execution = PydanticAiModelExecution(registry)

    conversation = ConversationSchema().with_request(
        MessageSchema.user_text("3000文字ぐらいの小説を書いて")
    )

    result = await execution.stream_text(
        conversation,
        StreamTextParams(
            key=AiModelKey.FAST,
            execution=AiExecutionContext(),
        ),
    )

    assert isinstance(result, Success)
    response = result.unwrap()

    async with response:
        async for message in response:
            print(message)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_stream_text_with_tool(registry: PydanticAiModelRegistry) -> None:

    execution = PydanticAiModelExecution(registry)

    async def get_value(
        input: GetValueInput,
        config: GetValueConfig | None,
    ) -> ToolResult[str]:
        if input.key != "customer_name":
            return ToolFailureResult(
                error=PublicError(
                    code="NOT_FOUND",
                    message="The requested value was not found.",
                    retryable=False,
                )
            )

        return ToolSuccessResult(
            data="value-for-customer_name",
        )

    tool = AiTool(
        name="get_value",
        description="Get a value by key.",
        input_type=GetValueInput,
        config=None,
        execute=get_value,
    )

    tool_config = ToolConfig(
        tool_loop_policy=ToolLoopPolicyMaxSteps(max_steps=1),
        tools=[tool],
    )

    conversation = ConversationSchema().with_request(
        MessageSchema.user_text(
            "get_valueツールを使ってcustomer_nameの値を取得してください。"
            "取得した値をそのまま回答してください。"
        )
    )

    result = await execution.stream_text(
        conversation,
        StreamTextParams(
            key=AiModelKey.FAST,
            execution=AiExecutionContext(),
            tool=tool_config,
        ),
    )

    assert isinstance(result, Success)

    response = result.unwrap()

    messages: list[str] = []

    async with response:
        async for message in response:
            messages.append(message)

    text = "".join(messages)

    assert text
    assert "value-for-customer_name" in text

    assert response.result
    print(response.result.message.text)
