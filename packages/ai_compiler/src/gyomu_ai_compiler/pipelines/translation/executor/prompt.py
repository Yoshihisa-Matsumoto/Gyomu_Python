from gyomu_ai_compiler.prompts.load import load_prompt
from gyomu_schema.error.translation import TranslationError
from gyomu_schema.schemas.document.content import DocumentContent
from gyomu_schema.schemas.document.section import (
    DocumentContentTranslationStrategy,
    LanguageCodes,
    SectionTranslationDefinition,
    SectionTranslationInstruction,
)
from gyomu_schema.schemas.document.validation import ValidationResult
from gyomu_schema.utility.context import caller_context
from gyomu_schema.utility.convert import to_json_schema
from gyomu_schema.utility.serialization import dump_json
from returns.result import Failure, Result, Success


def build_translation_prompt[TSchema: DocumentContent](
    language: LanguageCodes,
    section_id: str,
    context: TSchema,
    section_definition: SectionTranslationDefinition,
    content_strategy: DocumentContentTranslationStrategy[TSchema],
    validation_result: ValidationResult | None,
) -> Result[str, TranslationError]:

    prompt_result = load_prompt("document-translation.md")
    if isinstance(prompt_result, Failure):
        return prompt_result.alt(
            lambda error: TranslationError(
                "fail to build prompt message",
                phase="prompt",
                content_type=context.kind,
                section_id=section_id,
                context=caller_context(),
            ).chain(error)
        )

    section_instruction = (
        section_definition.translation_instruction + "\n\n"
        if isinstance(section_definition, SectionTranslationInstruction)
        and section_definition.translation_instruction is not None
        else ""
    ) + content_strategy.definition.translation_instruction

    prompt = (
        prompt_result.unwrap()
        .replace("{{SECTION_INSTRUCTION}}", section_instruction)
        .replace("{{TARGET_LANGUAGE}}", language)
        .replace(
            "{{INPUT_SCHEMA}}",
            to_json_schema(content_strategy.definition.content_schema),
        )
        .replace(
            "{{TRANSLATION_TARGETS}}",
            dump_json(value=context, model_type=type(context)),
        )
        .replace(
            "{{VALIDATION_ISSUES}}",
            ""
            if validation_result is None or validation_result.is_valid
            else "\n".join(
                f"- {issue.repair_instruction}" for issue in validation_result.issues
            ),
        )
    )
    return Success(prompt)
