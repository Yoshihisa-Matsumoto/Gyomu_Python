from pydantic_ai import ModelSettings

from gyomu_ai.execution.context import AiExecutionContext


def build_model_settings(
    execution_context: AiExecutionContext | None,
) -> ModelSettings | None:
    """Builds model settings from an AI execution context.

    Args:
        execution_context (AiExecutionContext | None): The AI execution context
            containing model configuration settings.

    Returns:
        ModelSettings | None: The built Pydantic AI ModelSettings dictionary, or None if
            no settings are present or context is None.
    """
    if execution_context is None:
        return None
    model_settings: ModelSettings = {}

    if execution_context.temperature is not None:
        model_settings["temperature"] = execution_context.temperature

    if execution_context.max_tokens is not None:
        model_settings["max_tokens"] = execution_context.max_tokens

    return model_settings or None
