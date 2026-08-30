from pathlib import Path

import pytest
from dotenv import load_dotenv
from gyomu_ai.provider.pydantic_ai.ai_model import PydanticAiModelRegistry
from gyomu_ai.provider.pydantic_ai.google import (
    create_default_pydantic_ai_model_registry,
)
from gyomu_schema.error.config import ConfigError

load_dotenv()


@pytest.fixture
def registry(project_dot_env: Path) -> PydanticAiModelRegistry:
    try:
        return create_default_pydantic_ai_model_registry(project_dot_env)
    except ConfigError:
        pytest.skip("GEMINI_API_KEY is not configured")
