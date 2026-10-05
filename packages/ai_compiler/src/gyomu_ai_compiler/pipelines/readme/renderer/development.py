from gyomu_ai_compiler.prompts.load import load_prompt
from gyomu_schema.conversation.conversation import ConversationSchema
from gyomu_schema.conversation.message import MessageSchema
from gyomu_schema.error.io import GyomuIOError
from gyomu_schema.schemas.concept.base import DocumentBaseContext
from returns.result import Failure, Result, Success


def build_development_messages(
    context: DocumentBaseContext,
) -> Result[ConversationSchema, GyomuIOError]:
    prompt_result = load_prompt(name="readme/development-assemble.md")
    if isinstance(prompt_result, Failure):
        return prompt_result

    final_prompt = (
        prompt_result.unwrap()
        .replace("{{MISSION}}", context.knowledge.package.mission)
        .replace(
            "{{RESPONSIBILITIES}}",
            "\n".join(f"- {r}" for r in context.concept.responsibilities),
        )
        .replace("{{POLICY}}", "\n".join(context.knowledge.package.policies))
    )
    conversation = ConversationSchema(request=MessageSchema.user_text(final_prompt))
    return Success(conversation)
