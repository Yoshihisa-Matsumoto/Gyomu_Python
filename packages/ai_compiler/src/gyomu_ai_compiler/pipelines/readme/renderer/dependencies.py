from gyomu_ai_compiler.prompts.load import load_prompt
from gyomu_schema.conversation.conversation import ConversationSchema
from gyomu_schema.conversation.message import MessageSchema
from gyomu_schema.error.io import GyomuIOError
from gyomu_schema.schemas.concept.base import DocumentBaseContext
from gyomu_schema.schemas.knowledge.technical import Compatibility, Dependency
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.utility.serialization import dump_json
from pydantic import BaseModel
from returns.result import Failure, Result, Success


class DirectorySummary(BaseModel):
    path: ProjectRelativePath
    summary: str
    responsibilities: list[str]
    relationships: list[str]


class UserData(BaseModel):
    dependencies: tuple[Dependency, ...]
    compatibility: tuple[Compatibility, ...]


def build_dependencies_messages(
    context: DocumentBaseContext,
) -> Result[ConversationSchema, GyomuIOError]:
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
