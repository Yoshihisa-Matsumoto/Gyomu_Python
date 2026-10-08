from gyomu_schema.conversation.conversation import ConversationSchema
from gyomu_schema.conversation.message import MessageSchema
from gyomu_schema.error.io import GyomuIOError
from gyomu_schema.schemas.concept.base import DocumentBaseContext, Knowledge
from gyomu_schema.schemas.knowledge.technical import Compatibility, Dependency
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.utility.serialization import dump_json
from pydantic import BaseModel
from returns.result import Failure, Result, Success

from gyomu_ai_compiler.prompts.load import load_prompt


class DirectorySummary(BaseModel):
    """Defines a directory summary containing its path, description,
    responsibilities, and relationships.
    """

    path: ProjectRelativePath
    """The project-relative path of the directory."""

    summary: str
    """A descriptive summary of the directory."""

    responsibilities: list[str]
    """List of responsibilities handled by the directory."""

    relationships: list[str]
    """List of relationships associated with the directory."""


class UserData(BaseModel):
    """Defines user data containing technical dependencies and compatibility
    information.
    """

    dependencies: tuple[Dependency, ...]
    """Collection of technical dependencies."""

    compatibility: tuple[Compatibility, ...]
    """Collection of compatibility rules and constraints."""


def build_dependencies_messages(
    context: DocumentBaseContext[Knowledge],
) -> Result[ConversationSchema, GyomuIOError]:
    """Builds conversation messages for technical dependencies and compatibility
    documentation.

    Args:
        context (DocumentBaseContext): The document base context containing knowledge
            and configuration.

    Returns:
        Result[ConversationSchema, GyomuIOError]: A Result containing the assembled
            conversation schema or a GyomuIOError on failure.
    """
    prompt_result = load_prompt(name="readme/dependencies-assemble.md")
    if isinstance(prompt_result, Failure):
        return prompt_result
    user_data = UserData(
        dependencies=context.knowledge.technical.dependencies,
        compatibility=context.knowledge.technical.compatibility,
    )
    conversation = ConversationSchema(
        system=MessageSchema.system_text(prompt_result.unwrap())
    ).with_request(
        MessageSchema.user_text(dump_json(user_data, indent=2, model_type=UserData))
    )
    return Success(conversation)
