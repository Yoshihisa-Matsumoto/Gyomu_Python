from gyomu_schema.conversation.conversation import ConversationSchema
from gyomu_schema.conversation.message import MessageSchema
from gyomu_schema.error.io import GyomuIOError
from gyomu_schema.schemas.concept.llm_context.input import LlmContextBuildContext
from gyomu_schema.utility.serialization import dump_json
from pydantic import BaseModel
from returns.result import Failure, Result, Success

from gyomu_ai_compiler.prompts.load import load_prompt


class UserData(BaseModel):
    """Represents user data containing policies, constraints, and rationale."""

    policies: tuple[str, ...]
    """Collection of policies."""

    constraints: tuple[str, ...]
    """Collection of constraints."""

    rationale: tuple[str, ...]
    """Collection of rationales."""


def build_design_principles_messages(
    context: LlmContextBuildContext,
) -> Result[ConversationSchema, GyomuIOError]:
    """Builds design principles conversation messages.

    Args:
        context (LlmContextBuildContext): The LLM context build context containing
            package knowledge.

    Returns:
        Result[ConversationSchema, GyomuIOError]: A Result containing the
            ConversationSchema on success or GyomuIOError on failure.
    """
    prompt_result = load_prompt(name="llm_context/design-principles.md")
    if isinstance(prompt_result, Failure):
        return prompt_result
    user_data = UserData(
        policies=context.knowledge.package.policies,
        constraints=context.knowledge.package.constraints,
        rationale=context.knowledge.package.rationale,
    )
    conversation = ConversationSchema(
        system=MessageSchema.system_text(prompt_result.unwrap())
    ).with_request(
        MessageSchema.user_text(dump_json(user_data, indent=2, model_type=UserData))
    )
    return Success(conversation)
