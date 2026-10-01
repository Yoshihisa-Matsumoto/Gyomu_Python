from gyomu_ai.execution.parameter import GenerateObjectParams
from gyomu_ai.model.ai_model import AiModelKey
from gyomu_ai.provider.pydantic_ai.route_service import PydanticAiRoutingExecution
from gyomu_ai_compiler.pipelines.document import DocumentRouteId
from gyomu_ai_compiler.pipelines.translation.executor.prompt import (
    build_translation_prompt,
)
from gyomu_schema.conversation.conversation import ConversationSchema
from gyomu_schema.conversation.message import MessageSchema
from gyomu_schema.error.translation import TranslationError
from gyomu_schema.schemas.document.content import DocumentContent
from gyomu_schema.schemas.document.section import (
    DocumentContentTranslationStrategy,
    LanguageCodes,
    SectionTranslationDefinition,
)
from gyomu_schema.schemas.document.validation import ValidationResult
from gyomu_schema.utility.context import caller_context
from returns.result import Failure, Result


async def translate_document_content[TSchema: DocumentContent](
    language: LanguageCodes,
    section_id: str,
    context: TSchema,
    section_definition: SectionTranslationDefinition,
    content_strategy: DocumentContentTranslationStrategy[TSchema],
    validation_result: ValidationResult | None,
) -> Result[TSchema, TranslationError]:
    prompt_result = build_translation_prompt(
        language,
        section_id,
        context,
        section_definition,
        content_strategy,
        validation_result,
    )
    if isinstance(prompt_result, Failure):
        return prompt_result

    conversation = ConversationSchema().with_request(
        MessageSchema.user_text(prompt_result.unwrap())
    )
    execution = PydanticAiRoutingExecution(route_id=DocumentRouteId)

    result = await execution.generate_object(
        conversation,
        GenerateObjectParams(
            key=AiModelKey.FAST,
            output_type=content_strategy.definition.content_schema,
        ),
    )

    return result.map(lambda response: response.output).alt(
        lambda error: TranslationError(
            "fail to translate",
            phase="translate",
            content_type=context.kind,
            section_id=section_id,
            context=caller_context(),
        ).chain(error)
    )
