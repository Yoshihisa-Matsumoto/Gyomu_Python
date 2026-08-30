import pytest
from gyomu_ai.execution.context import AiExecutionContext
from gyomu_ai.execution.parameter import (
    AiEmbeddingMode,
    EmbedParams,
)
from gyomu_ai.provider.pydantic_ai.ai_model import PydanticAiModelRegistry
from gyomu_ai.provider.pydantic_ai.execution import PydanticAiModelExecution

pytestmark = pytest.mark.integration


@pytest.mark.integration
@pytest.mark.asyncio
async def test_generate_text(registry: PydanticAiModelRegistry) -> None:

    execution = PydanticAiModelExecution(registry)

    result = await execution.embed(
        EmbedParams(
            mode=AiEmbeddingMode.QUERY,
            execution=AiExecutionContext(),
            value="Hello, I like banana.",
        ),
    )

    assert result
    response = result.unwrap()

    assert response.vector is not None
    assert response.metadata is not None
    print(response.vector)
    print(response.metadata)
