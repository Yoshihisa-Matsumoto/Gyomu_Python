from pathlib import Path

import pytest
from gyomu_ai.execution.context import AiExecutionContext
from gyomu_ai.execution.parameter import StreamTextParams
from gyomu_ai.model.ai_model import AiModelKey
from gyomu_ai.provider.pydantic_ai.execution import PydanticAiModelExecution
from gyomu_ai.provider.pydantic_ai.google import (
    create_default_pydantic_ai_model_registry,
)
from gyomu_schema.conversation.conversation import ConversationSchema
from gyomu_schema.conversation.message import MessageSchema
from returns.result import Success


@pytest.mark.integration
@pytest.mark.asyncio
async def test_stream_text(project_dot_env: Path) -> None:
    registry = create_default_pydantic_ai_model_registry(project_dot_env)

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
