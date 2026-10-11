from gyomu_schema.conversation.conversation import ConversationSchema
from gyomu_schema.conversation.message import MessageSchema
from gyomu_schema.error.io import GyomuIOError
from gyomu_schema.schemas.concept.llm_context.input import LlmContextBuildContext
from gyomu_schema.schemas.knowledge.coding_guideline import CodingRule
from gyomu_schema.utility.serialization import dump_json
from pydantic import BaseModel
from returns.result import Failure, Result, Success

from gyomu_ai_compiler.prompts.load import load_prompt


class UserData(BaseModel):
    """Represents user data containing coding rules and forbidden patterns."""

    rules: tuple[CodingRule, ...]
    """Tuple of coding rules."""

    forbidden: tuple[str, ...]
    """Tuple of forbidden patterns or strings."""


def build_editing_rule_messages(
    context: LlmContextBuildContext,
) -> Result[ConversationSchema, GyomuIOError]:
    """Builds editing rule messages from the LLM context.

    Args:
        context (LlmContextBuildContext): The LLM context build context containing
            knowledge and configuration.

    Returns:
        Result[ConversationSchema, GyomuIOError]: A result containing the conversation
            schema or an IO error.
    """
    prompt_result = load_prompt(name="llm_context/editing-rule.md")
    if isinstance(prompt_result, Failure):
        return prompt_result
    user_data = UserData(
        rules=context.knowledge.coding_guideline.rules,
        forbidden=context.knowledge.coding_guideline.forbidden,
    )
    conversation = ConversationSchema(
        system=MessageSchema.system_text(prompt_result.unwrap())
    ).with_request(
        MessageSchema.user_text(dump_json(user_data, indent=2, model_type=UserData))
    )
    return Success(conversation)
