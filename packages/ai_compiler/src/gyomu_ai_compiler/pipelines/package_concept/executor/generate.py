from gyomu_ai.execution.parameter import GenerateObjectParams
from gyomu_ai.model.ai_model import AiModelKey
from gyomu_ai.provider.pydantic_ai.route_service import PydanticAiRoutingExecution
from gyomu_ai_compiler.pipelines.document import DocumentRouteId
from gyomu_ai_compiler.pipelines.package_concept.renderer.package_analysis import (
    render_package_analysis,
)
from gyomu_ai_compiler.prompts.load import load_prompt
from gyomu_schema.conversation.conversation import ConversationSchema
from gyomu_schema.conversation.message import MessageSchema
from gyomu_schema.error.ai import AiError
from gyomu_schema.error.io import GyomuIOError
from gyomu_schema.schemas.concept.package.analysis import PackageAnalysis
from gyomu_schema.schemas.concept.package.concept import PackageConcept
from returns.result import Failure, Result


async def generate_package_concept(
    context: PackageAnalysis,
) -> Result[PackageConcept, GyomuIOError | AiError]:
    prompt_result = load_prompt("package-concept.md")
    if isinstance(prompt_result, Failure):
        return prompt_result
    prompt = prompt_result.unwrap().replace(
        "<##PACKAGE##>",
        render_package_analysis(context),
    )

    conversation = ConversationSchema().with_request(MessageSchema.user_text(prompt))
    execution = PydanticAiRoutingExecution(route_id=DocumentRouteId)

    result = await execution.generate_object(
        conversation,
        GenerateObjectParams(
            key=AiModelKey.FAST,
            output_type=PackageConcept,
        ),
    )

    return result.map(lambda response: response.output)
