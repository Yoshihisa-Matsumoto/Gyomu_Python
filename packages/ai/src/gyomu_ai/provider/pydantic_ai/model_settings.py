from gyomu_ai.execution.context import AiExecutionContext
from pydantic_ai import ModelSettings


def build_model_settings(
    execution_context: AiExecutionContext | None,
) -> ModelSettings | None:
    if execution_context is None:
        return None
    model_settings: ModelSettings = {}

    if execution_context.temperature is not None:
        model_settings["temperature"] = execution_context.temperature

    if execution_context.max_tokens is not None:
        model_settings["max_tokens"] = execution_context.max_tokens

    return model_settings or None
