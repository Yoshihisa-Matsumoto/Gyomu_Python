from pathlib import Path

import pytest
from gyomu_ai.execution.context import AiExecutionContext
from gyomu_ai.execution.parameter import GenerateObjectParams
from gyomu_ai.model.ai_model import AiModelKey
from gyomu_ai.provider.pydantic_ai.execution import PydanticAiModelExecution
from gyomu_ai.provider.pydantic_ai.google import (
    create_default_pydantic_ai_model_registry,
)
from gyomu_schema.conversation.conversation import ConversationSchema
from gyomu_schema.conversation.message import MessageSchema
from pydantic import BaseModel

pytestmark = pytest.mark.integration


class UserSchema(BaseModel):
    name: str
    age: int


@pytest.mark.integration
@pytest.mark.asyncio
async def test_generate_object(project_dot_env: Path) -> None:
    registry = create_default_pydantic_ai_model_registry(project_dot_env)

    execution = PydanticAiModelExecution(registry)

    conversation = ConversationSchema().with_request(
        MessageSchema.user_text("""Return a json object:
  name = john
  age = 20""")
    )

    result = await execution.generate_object(
        conversation,
        GenerateObjectParams(
            key=AiModelKey.FAST,
            output_type=UserSchema,
            execution=AiExecutionContext(),
        ),
    )

    assert result
    response = result.unwrap()

    assert response is not None
    assert isinstance(response.output, UserSchema)
    print(response)
