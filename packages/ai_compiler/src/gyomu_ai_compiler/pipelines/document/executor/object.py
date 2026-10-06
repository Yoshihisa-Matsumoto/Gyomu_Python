from gyomu_ai.execution.parameter import GenerateObjectParams
from gyomu_ai.model.ai_model import AiModelKey
from gyomu_ai.provider.pydantic_ai.route_service import PydanticAiRoutingExecution
from gyomu_schema.error.ai import AiError
from gyomu_schema.error.io import GyomuIOError
from gyomu_schema.schemas.document.section import SectionPromptProvider
from pydantic import BaseModel
from returns.result import Failure, Result

from gyomu_ai_compiler.pipelines.document import DocumentRouteId


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
    """Build a section object using AI generation.

    Builds a structured section object using an AI model based on the provided section
    ID, context, and schema.

    Args:
        section_id (TSectionId): The identifier of the section being built.
        context (TContext): The context data used to render the section prompt.
        provider (SectionPromptProvider[TSectionId, TContext]): The provider responsible
            for rendering the section prompt.
        schema (type[TSchema]): The Pydantic schema class defining the expected output
            structure.

    Returns:
        Result[TSchema, GyomuIOError | AiError]: A Result containing the parsed schema
            instance on success, or a GyomuIOError or AiError on failure.
    """
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
