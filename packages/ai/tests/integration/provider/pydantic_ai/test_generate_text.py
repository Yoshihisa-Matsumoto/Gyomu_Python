from pathlib import Path

import pytest
from gyomu_ai.execution.context import AiExecutionContext
from gyomu_ai.execution.parameter import GenerateTextParams
from gyomu_ai.model.ai_model import AiModelKey
from gyomu_ai.provider.pydantic_ai.execution import PydanticAiModelExecution
from gyomu_ai.provider.pydantic_ai.google import (
    create_default_pydantic_ai_model_registry,
)
from gyomu_schema.conversation.conversation import ConversationSchema
from gyomu_schema.conversation.message import MessageSchema


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
