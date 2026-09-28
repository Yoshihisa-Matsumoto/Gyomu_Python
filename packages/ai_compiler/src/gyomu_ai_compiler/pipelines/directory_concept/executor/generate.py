from gyomu_ai.execution.parameter import GenerateObjectParams
from gyomu_ai.model.ai_model import AiModelKey
from gyomu_ai.provider.pydantic_ai.route_service import PydanticAiRoutingExecution
from gyomu_schema.conversation.conversation import ConversationSchema
from gyomu_schema.conversation.message import MessageSchema
from gyomu_schema.error.ai import AiError
from gyomu_schema.error.io import GyomuIOError
from gyomu_schema.schemas.concept.directory.concept import DirectoryConcept
from gyomu_schema.schemas.concept.directory.input import DirectoryConceptInput
from returns.result import Failure, Result

from gyomu_ai_compiler.pipelines.directory_concept.renderer.file_summary import (
    render_file_summary,
)
from gyomu_ai_compiler.pipelines.directory_concept.renderer.sub_directory import (
    render_sub_directory,
)
from gyomu_ai_compiler.pipelines.document import DocumentRouteId
from gyomu_ai_compiler.prompts.load import load_prompt


async def generate_directory_concept(
    context: DirectoryConceptInput,
) -> Result[DirectoryConcept, GyomuIOError | AiError]:
    prompt_result = load_prompt("directory-concept.md")
    if isinstance(prompt_result, Failure):
        return prompt_result
    prompt = (
        prompt_result.unwrap()
        .replace(
            "<##FILES##>",
            "\n\n".join(render_file_summary(file) for file in context.files),
        )
        .replace(
            "<##DIRECTORIES##>",
            "\n\n".join(
                render_sub_directory(directory) for directory in context.sub_directories
            ),
        )
    )

    conversation = ConversationSchema().with_request(MessageSchema.user_text(prompt))
    execution = PydanticAiRoutingExecution(route_id=DocumentRouteId)

    result = await execution.generate_object(
        conversation,
        GenerateObjectParams(
            key=AiModelKey.FAST,
            output_type=DirectoryConcept,
        ),
    )

    return result.map(lambda response: response.output)
