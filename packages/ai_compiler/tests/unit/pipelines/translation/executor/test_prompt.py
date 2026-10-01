from unittest.mock import patch

from gyomu_ai_compiler.pipelines.translation.executor.prompt import (
    build_translation_prompt,
)
from gyomu_schema.error.io import GyomuIOError, IOLayer, IOOperation
from gyomu_schema.error.translation import TranslationError
from gyomu_schema.schemas.document.translation.paragraph import (
    paragraph_translation_strategy,
)
from returns.result import Failure, Success

from packages.schema.schema_test_support.concept_helpers import (
    create_paragraph,
    create_section_translation,
    create_validation_issue,
    create_validation_result,
)


def test_build_translation_prompt_success() -> None:
    context = create_paragraph()

    section_definition = create_section_translation(
        no_translation=True,
    )

    strategy = paragraph_translation_strategy

    with patch(
        "gyomu_ai_compiler.pipelines.translation.executor.prompt.load_prompt",
        return_value=Success(
            "section={{SECTION_INSTRUCTION}}\n"
            "language={{TARGET_LANGUAGE}}\n"
            "schema={{INPUT_SCHEMA}}\n"
            "targets={{TRANSLATION_TARGETS}}\n"
            "issues={{VALIDATION_ISSUES}}"
        ),
    ):
        result = build_translation_prompt(
            language="ja",
            section_id="description",
            context=context,
            section_definition=section_definition,
            content_strategy=strategy,
            validation_result=None,
        )

    assert isinstance(result, Success)

    prompt = result.unwrap()

    assert "language=ja" in prompt
    assert "{{SECTION_INSTRUCTION}}" not in prompt
    assert "{{TARGET_LANGUAGE}}" not in prompt
    assert "{{INPUT_SCHEMA}}" not in prompt
    assert "{{TRANSLATION_TARGETS}}" not in prompt
    assert "{{VALIDATION_ISSUES}}" not in prompt


def test_build_translation_prompt_includes_section_and_content_instruction() -> None:
    context = create_paragraph()

    section_definition = create_section_translation(
        no_translation=False,
        translation_instruction="Translate the section naturally.",
    )

    strategy = paragraph_translation_strategy

    with patch(
        "gyomu_ai_compiler.pipelines.translation.executor.prompt.load_prompt",
        return_value=Success("{{SECTION_INSTRUCTION}}"),
    ):
        result = build_translation_prompt(
            language="ja",
            section_id="description",
            context=context,
            section_definition=section_definition,
            content_strategy=paragraph_translation_strategy,
            validation_result=None,
        )

    assert isinstance(result, Success)
    assert (
        result.unwrap()
        == "Translate the section naturally.\n\n"
        + strategy.definition.translation_instruction
    )


def test_build_translation_prompt_includes_validation_issues() -> None:
    context = create_paragraph()

    section_definition = create_section_translation()

    # strategy = create_paragraph_translation_strategy()

    validation_result = create_validation_result(
        issues=(
            create_validation_issue(
                code="invalid-content",
                repair_instruction="Translate the content completely.",
            ),
            create_validation_issue(
                code="invalid-format",
                repair_instruction="Preserve the original structure.",
            ),
        )
    )

    with patch(
        "gyomu_ai_compiler.pipelines.translation.executor.prompt.load_prompt",
        return_value=Success("{{VALIDATION_ISSUES}}"),
    ):
        result = build_translation_prompt(
            language="ja",
            section_id="description",
            context=context,
            section_definition=section_definition,
            content_strategy=paragraph_translation_strategy,
            validation_result=validation_result,
        )

    assert isinstance(result, Success)
    assert result.unwrap() == (
        "- Translate the content completely.\n- Preserve the original structure."
    )


def test_build_translation_prompt_omits_validation_issues_when_valid() -> None:
    context = create_paragraph()

    section_definition = create_section_translation()
    strategy = paragraph_translation_strategy

    validation_result = create_validation_result()

    with patch(
        "gyomu_ai_compiler.pipelines.translation.executor.prompt.load_prompt",
        return_value=Success("{{VALIDATION_ISSUES}}"),
    ):
        result = build_translation_prompt(
            language="ja",
            section_id="description",
            context=context,
            section_definition=section_definition,
            content_strategy=strategy,
            validation_result=validation_result,
        )

    assert isinstance(result, Success)
    assert result.unwrap() == ""


def test_build_translation_prompt_returns_translation_error_when_loading_prompt_fails() -> (
    None
):
    context = create_paragraph()

    section_definition = create_section_translation()
    strategy = paragraph_translation_strategy

    original_error = GyomuIOError(
        "test",
        layer=IOLayer.FILESYSTEM,
        operation=IOOperation.READ,
    )

    with patch(
        "gyomu_ai_compiler.pipelines.translation.executor.prompt.load_prompt",
        return_value=Failure(original_error),
    ):
        result = build_translation_prompt(
            language="ja",
            section_id="description",
            context=context,
            section_definition=section_definition,
            content_strategy=strategy,
            validation_result=None,
        )

    assert isinstance(result, Failure)

    error = result.failure()

    assert isinstance(error, TranslationError)
    assert error.phase == "prompt"
    assert error.content_type == context.kind
    assert error.section_id == "description"
