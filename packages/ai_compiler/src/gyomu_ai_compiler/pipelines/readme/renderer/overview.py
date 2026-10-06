from gyomu_schema.conversation.conversation import ConversationSchema
from gyomu_schema.conversation.message import MessageSchema
from gyomu_schema.error.io import GyomuIOError
from gyomu_schema.schemas.concept.base import DocumentBaseContext
from gyomu_schema.utility.serialization import dump_json
from pydantic import BaseModel
from returns.result import Failure, Result, Success

from gyomu_ai_compiler.prompts.load import load_prompt


class UserData(BaseModel):
    """Represents user data containing a mission and concept summary for overview
    generation.

    Represents user data containing the mission and concept summary for overview
    generation.
    """

    mission: str
    """The mission statement for the package."""

    concept_summary: str
    """A summary of the concept."""


def build_overview_messages(
    context: DocumentBaseContext,
) -> Result[ConversationSchema, GyomuIOError]:
    """Builds conversation messages for overview generation.

    Constructs the conversation messages for generating the overview section of the
    README.

    Args:
        context (DocumentBaseContext): The document base context containing knowledge
            and concept information.

    Returns:
        Result[ConversationSchema, GyomuIOError]: A Result containing either the
            ConversationSchema conversation or a GyomuIOError.
    """
    prompt_result = load_prompt(name="readme/overview-generate.md")
    if isinstance(prompt_result, Failure):
        return prompt_result
    user_data = UserData(
        mission=context.knowledge.package.mission,
        concept_summary=context.concept.summary,
    )
    conversation = ConversationSchema(
        system=MessageSchema.system_text(prompt_result.unwrap())
    ).with_request(
        MessageSchema.user_text(dump_json(user_data, indent=2, model_type=UserData))
    )
    return Success(conversation)
