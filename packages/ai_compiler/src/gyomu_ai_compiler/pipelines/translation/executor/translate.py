from gyomu_ai.execution.parameter import GenerateObjectParams
from gyomu_ai.model.ai_model import AiModelKey
from gyomu_ai.provider.pydantic_ai.route_service import PydanticAiRoutingExecution
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
from returns.result import Failure, Result, Success

from gyomu_ai_compiler.pipelines.document import DocumentRouteId
from gyomu_ai_compiler.pipelines.translation.executor.prompt import (
    build_translation_prompt,
)


async def translate_document_content[TSchema: DocumentContent](
    language: LanguageCodes,
    section_id: str,
    context: TSchema,
    section_definition: SectionTranslationDefinition,
    content_strategy: DocumentContentTranslationStrategy[TSchema],
    validation_result: ValidationResult | None,
) -> Result[TSchema, TranslationError]:
    """Translate document content using AI routing execution based on the provided
    strategy and definitions.

    Args:
        language (LanguageCodes): Target language code for the translation.
        section_id (str): Identifier of the section being translated.
        context (TSchema): Document content context to be translated.
        section_definition (SectionTranslationDefinition): Definition rules for section
            translation.
        content_strategy (DocumentContentTranslationStrategy[TSchema]): Translation
            strategy specifying content handling and schemas.
        validation_result (ValidationResult | None): Optional validation result from
            previous pipeline steps.

    Returns:
        Result[TSchema, TranslationError]: A Result containing the translated document
            content schema on success, or a TranslationError on failure.
    """
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
    if isinstance(result, Success):
        print("Input")
        if conversation.request:
            print(repr(conversation.request.parts[0].text))
        print("Output")
        print(repr(result.unwrap().output))

    return result.map(lambda response: response.output).alt(
        lambda error: TranslationError(
            "fail to translate",
            phase="translate",
            content_type=context.kind,
            section_id=section_id,
            context=caller_context(),
        ).chain(error)
    )
