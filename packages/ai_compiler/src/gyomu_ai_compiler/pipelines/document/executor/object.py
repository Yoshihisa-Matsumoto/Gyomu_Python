from gyomu_ai.execution.parameter import GenerateObjectParams
from gyomu_ai.model.ai_model import AiModelKey
from gyomu_ai.provider.pydantic_ai.route_service import PydanticAiRoutingExecution
from gyomu_ai_compiler.pipelines.document import DocumentRouteId
from gyomu_schema.error.ai import AiError
from gyomu_schema.error.io import GyomuIOError
from gyomu_schema.schemas.document.section import SectionPromptProvider
from pydantic import BaseModel
from returns.result import Failure, Result


async def build_section_object[
    TSectionId: str,
    TContext: BaseModel,
    TSchema: BaseModel,
](
    section_id: TSectionId,
    context: TContext,
    provider: SectionPromptProvider[TSectionId, TContext],
    schema: type[TSchema],
) -> Result[TSchema, GyomuIOError | AiError]:
    execution = PydanticAiRoutingExecution(route_id=DocumentRouteId)
    render_result = provider.render(section_id, context)

    if isinstance(render_result, Failure):
        return render_result

    conversation = render_result.unwrap()

    result = await execution.generate_object(
        conversation=conversation,
        params=GenerateObjectParams(
            key=AiModelKey.FAST,
            output_type=schema,
        ),
    )
    return result.map(lambda response: response.output)
