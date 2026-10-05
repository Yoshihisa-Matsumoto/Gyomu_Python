from gyomu_ai_compiler.prompts.load import load_prompt
from gyomu_facts.package.analysis import PackageFacts, TopScoreDirectorySelection
from gyomu_schema.conversation.conversation import ConversationSchema
from gyomu_schema.conversation.message import MessageSchema
from gyomu_schema.error.io import GyomuIOError
from gyomu_schema.schemas.concept.base import DocumentBaseContext
from gyomu_schema.schemas.concept.package.concept import CapabilityConcept
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
    concept_summary: str
    responsibilities: list[str]
    capabilities: list[CapabilityConcept]
    directories: list[DirectorySummary]


def build_architecture_messages(
    context: DocumentBaseContext,
) -> Result[ConversationSchema, GyomuIOError]:
    prompt_result = load_prompt(name="readme/architecture-generate.md")
    if isinstance(prompt_result, Failure):
        return prompt_result

    target_directories = PackageFacts(context.analysis).get_ranked_directories(
        TopScoreDirectorySelection(limit=5)
    )

    user_data = UserData(
        concept_summary=context.concept.summary,
        responsibilities=context.concept.responsibilities,
        capabilities=context.concept.capabilities,
        directories=[
            DirectorySummary(
                path=directory.path,
                summary=directory.concept.summary,
                responsibilities=directory.concept.responsibilities,
                relationships=directory.concept.relationships,
            )
            for directory in target_directories
        ],
    )
    conversation = ConversationSchema(
        system=MessageSchema.system_text(prompt_result.unwrap())
    ).with_request(
        MessageSchema.user_text(dump_json(user_data, indent=2, model_type=UserData))
    )
    return Success(conversation)
