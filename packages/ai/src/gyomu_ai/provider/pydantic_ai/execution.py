from gyomu_ai.execution.context import AiModelContext
from gyomu_ai.execution.parameter import GenerateTextParams
from gyomu_ai.execution.result import AiGenerateTextResult
from gyomu_ai.model.ai_model import AiModelKey, AiModelRegistry
from gyomu_ai.provider.pydantic_ai.build_prompt import build_prompt
from gyomu_ai.provider.pydantic_ai.map_result import map_generate_text_result
from gyomu_schema.conversation.conversation import ConversationSchema
from gyomu_schema.error.ai import AiError
from pydantic_ai import Agent, ModelSettings
from returns.result import Result, Success


class PydanticAiModelExecution:
    def __init__(
        self,
        registry: AiModelRegistry[
            Agent,
            Agent,
        ],
    ) -> None:
        self._registry = registry

    def _select_agent(self, key: AiModelKey, context: AiModelContext) -> Agent:
        match key:
            case AiModelKey.FAST:
                return self._registry.fast(context)
            case AiModelKey.SMART:
                return self._registry.smart(context)
            case AiModelKey.REASONING:
                return self._registry.reasoning(context)
            case AiModelKey.VISION:
                return self._registry.vision(context)
            case AiModelKey.EMBEDDING:
                raise ValueError("Embedding model cannot be used for text generation")

    async def generate_text(
        self,
        conversation: ConversationSchema,
        params: GenerateTextParams,
    ) -> Result[AiGenerateTextResult, AiError]:
        agent = self._select_agent(params.key, params.execution)
        prompt = build_prompt(conversation)
        model_settings: ModelSettings | None = (
            {"temperature": params.execution.temperature}
            if params.execution.temperature
            else None
        )
        response = await agent.run(
            instructions=prompt.instructions,
            user_prompt=prompt.user_prompt,
            message_history=prompt.message_history,
            model_settings=model_settings,
        )

        return Success(map_generate_text_result(response))
