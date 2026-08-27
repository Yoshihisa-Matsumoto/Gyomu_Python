# from gyomu_schema.error.ai import AiError
# from instructor import AsyncInstructor, from_provider
# from returns.result import Result, Success

# from gyomu_ai.execution.parameter import GenerateTextParams
# from gyomu_ai.execution.result import AiAssistantMessage, AiGenerateTextResult
# from gyomu_ai.model.ai_model import AiModelKey, AiModelRegistry
# from gyomu_ai.provider.instructor.build_prompt import build_prompt

# client = from_provider("google/gemini-3.5-flash-lite", async_client=True)


# class InstructorAiModelExecution:
#     def __init__(
#         self,
#         registry: AiModelRegistry[
#             AsyncInstructor,
#             AsyncInstructor,
#         ],
#     ) -> None:
#         self._registry = registry

#     def _select_model(
#         self,
#         key: AiModelKey,
#     ) -> AsyncInstructor:
#         match key:
#             case AiModelKey.FAST:
#                 return self._registry.fast
#             case AiModelKey.SMART:
#                 return self._registry.smart
#             case AiModelKey.REASONING:
#                 return self._registry.reasoning
#             case AiModelKey.VISION:
#                 return self._registry.vision
#             case AiModelKey.EMBEDDING:
#                 raise ValueError("Embedding model cannot be used for text generation")

#     async def generate_text(
#         self,
#         params: GenerateTextParams,
#     ) -> Result[AiGenerateTextResult, AiError]:
#         model = self._select_model(params.key)

#         response = await model.chat.completions.create_with_completion(
#             messages=build_prompt(params.messages),
#             temperature=params.execution.temperature,
#             max_tokens=params.max_tokens,
#         )

#         return Success(
#             AiGenerateTextResult(
#                 message=AiAssistantMessage(text=response), finish_reason="completed"
#             )
#         )
