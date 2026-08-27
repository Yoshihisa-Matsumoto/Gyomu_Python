from collections.abc import Callable

from gyomu_ai.execution.context import AiModelContext
from gyomu_ai.provider.pydantic_ai.ai_model import PydanticAiModelRegistry
from gyomu_infra.config.loader import ConfigLoader
from gyomu_schema.config.config_loader_option import EnvironmentLoaderOption
from pydantic import BaseModel
from pydantic_ai import Agent, Embedder
from pydantic_ai.embeddings.google import GoogleEmbeddingModel, GoogleEmbeddingModelName
from pydantic_ai.models.google import GoogleModel, GoogleModelName
from pydantic_ai.providers.google import GoogleProvider
from returns.result import Failure


class GoogleAPIConfig(BaseModel):
    api_key: str


def create_google_agent(
    model_name: GoogleModelName,
    setting: GoogleAPIConfig,
) -> Callable[[AiModelContext], Agent]:
    def factory(context: AiModelContext) -> Agent:
        return Agent(
            model=GoogleModel(
                model_name,
                provider=GoogleProvider(
                    api_key=setting.api_key,
                ),
            ),
        )

    return factory


def create_google_embedding(
    model_name: GoogleEmbeddingModelName,
    setting: GoogleAPIConfig,
) -> Callable[[AiModelContext], Embedder]:
    def factory(context: AiModelContext) -> Embedder:

        model = GoogleEmbeddingModel(
            model_name=model_name,
            provider=GoogleProvider(
                api_key=setting.api_key,
            ),
        )
        return Embedder(model=model)

    return factory


def create_pydantic_ai_model_registry(
    setting: GoogleAPIConfig,
) -> PydanticAiModelRegistry:
    return PydanticAiModelRegistry(
        fast=create_google_agent(
            "gemini-3.5-flash-lite",
            setting=setting,
        ),
        smart=create_google_agent(
            "gemini-3.5-flash-lite",
            setting=setting,
        ),
        reasoning=create_google_agent(
            "gemini-3.5-flash-lite",
            setting=setting,
        ),
        vision=create_google_agent(
            "gemini-3.5-flash-lite",
            setting=setting,
        ),
        embedding=create_google_embedding(
            "gemini-embedding-001",
            setting=setting,
        ),
    )


def create_default_pydantic_ai_model_registry() -> PydanticAiModelRegistry:
    setting_result = ConfigLoader.load(
        GoogleAPIConfig,
        EnvironmentLoaderOption(
            variables={"GEMINI_API_KEY": "api_key"},
        ),
    )

    if isinstance(setting_result, Failure):
        raise setting_result.failure()

    return create_pydantic_ai_model_registry(
        setting_result.unwrap(),
    )
