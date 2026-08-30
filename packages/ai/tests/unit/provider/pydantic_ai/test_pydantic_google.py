from pathlib import Path

import pytest
from gyomu_ai.execution.context import AiModelContext
from gyomu_ai.provider.pydantic_ai.ai_model import PydanticAiModelRegistry
from gyomu_ai.provider.pydantic_ai.google import (
    GoogleAPIConfig,
    create_default_pydantic_ai_model_registry,
    create_google_embedding,
    create_google_model,
    create_pydantic_ai_model_registry,
)
from gyomu_schema.error.config import ConfigError
from pydantic_ai import Embedder
from pydantic_ai.embeddings.google import GoogleEmbeddingModel
from pydantic_ai.models import Model


class TestCreateGoogleAgent:
    def test_creates_model(self) -> None:
        factory = create_google_model(
            "gemini-3.5-flash-lite",
            GoogleAPIConfig(api_key="test-api-key"),
        )

        model = factory(AiModelContext())

        assert isinstance(model, Model)


class TestCreateGoogleEmbedding:
    def test_creates_embedder(self) -> None:
        factory = create_google_embedding(
            "gemini-embedding-001",
            GoogleAPIConfig(api_key="test-api-key"),
        )

        embedder = factory(AiModelContext())

        assert isinstance(embedder, Embedder)
        assert isinstance(embedder.model, GoogleEmbeddingModel)


class TestCreatePydanticAiModelRegistry:
    def test_creates_registry(
        self,
    ) -> None:
        setting = GoogleAPIConfig(
            api_key="test-api-key",
        )

        registry = create_pydantic_ai_model_registry(setting)

        assert isinstance(registry, PydanticAiModelRegistry)

        assert isinstance(
            registry.fast(AiModelContext()),
            Model,
        )
        assert isinstance(
            registry.smart(AiModelContext()),
            Model,
        )
        assert isinstance(
            registry.reasoning(AiModelContext()),
            Model,
        )
        assert isinstance(
            registry.vision(AiModelContext()),
            Model,
        )
        assert isinstance(
            registry.embedding(AiModelContext()),
            Embedder,
        )


class TestCreateDefaultPydanticAiModelRegistry:
    def test_creates_registry(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv(
            "GEMINI_API_KEY",
            "test-api-key",
        )

        registry = create_default_pydantic_ai_model_registry()

        assert isinstance(registry, PydanticAiModelRegistry)

    def test_raises_when_api_key_is_missing(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        monkeypatch.delenv(
            "GEMINI_API_KEY",
            raising=False,
        )

        with pytest.raises(ConfigError):
            create_default_pydantic_ai_model_registry(dot_env_path=tmp_path / ".env")
