from pathlib import Path

import pytest
from gyomu_ai.execution.context import AiExecutionContext
from gyomu_ai.execution.parameter import (
    GenerateTextParams,
    ToolConfig,
    ToolLoopPolicyMaxSteps,
)
from gyomu_ai.model.ai_model import AiModelKey
from gyomu_ai.provider.pydantic_ai.execution import PydanticAiModelExecution
from gyomu_ai.provider.pydantic_ai.google import (
    create_default_pydantic_ai_model_registry,
)
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

pytestmark = pytest.mark.integration


@pytest.mark.integration
@pytest.mark.asyncio
async def test_generate_text(project_dot_env: Path) -> None:
    registry = create_default_pydantic_ai_model_registry(project_dot_env)

    execution = PydanticAiModelExecution(registry)

    conversation = ConversationSchema().with_request(
        MessageSchema.user_text("こんにちは。短く自己紹介してください。")
    )

    result = await execution.generate_text(
        conversation,
        GenerateTextParams(
            key=AiModelKey.FAST,
            execution=AiExecutionContext(),
        ),
    )

    assert result
    response = result.unwrap()

    assert response.message.text
    assert response.metadata is not None
    assert response.metadata.usage.input_tokens > 0
    assert response.metadata.usage.output_tokens > 0
    print(response.message.text)
    print(response.metadata)


class GetValueInput(BaseModel):
    key: str


tool_calls: list[GetValueInput] = []


async def get_value(
    input: GetValueInput,
    config: GetValueInput | None,
) -> ToolResult[str]:
    tool_calls.append(input)

    return ToolSuccessResult(
        data=f"value-for-{input.key}",
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_generate_text_with_tool(
    project_dot_env: Path,
) -> None:
    registry = create_default_pydantic_ai_model_registry(project_dot_env)

    execution = PydanticAiModelExecution(registry)

    tool = AiTool(
        name="get_value",
        description="Gets a value for the specified key.",
        input_type=GetValueInput,
        config=None,
        execute=get_value,
    )

    conversation = ConversationSchema().with_request(
        MessageSchema.user_text(
            """
            必ず get_value ツールを使ってください。
            key に "customer_name" を指定して値を取得し、
            Toolから返された値をそのまま回答してください。
            """
        )
    )

    result = await execution.generate_text(
        conversation,
        GenerateTextParams(
            key=AiModelKey.FAST,
            execution=AiExecutionContext(),
            tool=ToolConfig(
                tool_loop_policy=ToolLoopPolicyMaxSteps(
                    max_steps=1,
                ),
                tools=[tool],
            ),
        ),
    )

    assert result

    response = result.unwrap()

    assert response.message.text
    assert "value-for-customer_name" in response.message.text

    assert response.metadata is not None
    assert response.metadata.usage.input_tokens > 0
    assert response.metadata.usage.output_tokens > 0

    print(response.message.text)
    print(response.metadata)

    assert len(tool_calls) == 1
    assert tool_calls[0] == GetValueInput(
        key="customer_name",
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_generate_text_with_tool_failure(
    project_dot_env: Path,
) -> None:
    registry = create_default_pydantic_ai_model_registry(project_dot_env)

    execution = PydanticAiModelExecution(registry)

    class GetValueInput(BaseModel):
        key: str

    class TestToolConfig(BaseModel):
        pass

    tool_calls: list[GetValueInput] = []

    async def get_value(
        input: GetValueInput,
        config: TestToolConfig | None,
    ) -> ToolResult[str]:
        tool_calls.append(input)

        return ToolFailureResult(
            error=PublicError(
                code="NOT_ALLOWED",
                message="The requested value cannot be accessed.",
                retryable=False,
            ),
        )

    tool = AiTool(
        name="get_value",
        description="Gets a value for the specified key.",
        input_type=GetValueInput,
        config=None,
        execute=get_value,
    )

    conversation = ConversationSchema().with_request(
        MessageSchema.user_text(
            """
            必ず get_value ツールを使ってください。
            key に "customer_name" を指定して値を取得してください。

            Toolがエラーを返した場合は、
            そのエラーの内容を簡潔に説明してください。
            """
        )
    )

    result = await execution.generate_text(
        conversation,
        GenerateTextParams(
            key=AiModelKey.FAST,
            execution=AiExecutionContext(),
            tool=ToolConfig(
                tool_loop_policy=ToolLoopPolicyMaxSteps(
                    max_steps=1,
                ),
                tools=[tool],
            ),
        ),
    )

    assert result

    response = result.unwrap()

    assert response.message.text

    assert len(tool_calls) == 1
    assert tool_calls[0] == GetValueInput(
        key="customer_name",
    )

    assert response.message.text
    assert len(tool_calls) == 1

    assert "NOT_ALLOWED" in response.message.text

    assert response.metadata is not None
    assert response.metadata.usage.input_tokens > 0
    assert response.metadata.usage.output_tokens > 0

    print(response.message.text)
    print(response.metadata)
