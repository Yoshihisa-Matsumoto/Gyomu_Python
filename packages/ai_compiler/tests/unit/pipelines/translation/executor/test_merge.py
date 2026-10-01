from gyomu_ai_compiler.pipelines.translation.executor.merge import (
    merge_retry_context,
)
from gyomu_schema.error.translation import TranslationError
from gyomu_schema.schemas.document.content import Paragraph
from gyomu_schema.schemas.document.section import (
    RetryContextArg,
    TranslationState,
)
from gyomu_schema.schemas.document.translation.paragraph import (
    paragraph_translation_strategy,
)
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.schema.schema_test_support.concept_helpers import (
    create_paragraph,
    create_section_translation,
    create_validation_issue,
    create_validation_result,
)


class TestMergeRetryContext:
    def test_returns_failure_when_current_validation_is_valid(self) -> None:
        original_context = create_paragraph()
        translated_context = create_paragraph("translated")

        strategy = paragraph_translation_strategy
        current_validation = create_validation_result()

        result = merge_retry_context(
            section_id="description",
            section_definition=create_section_translation(),
            content_strategy=strategy,
            current_validation=current_validation,
            previous_validation=None,
            original_context=original_context,
            translated_context=translated_context,
        )

        assert isinstance(result, Failure)

        error = result.failure()

        assert isinstance(error, TranslationError)
        assert error.phase == "retry-context"
        assert error.content_type == original_context.kind
        assert error.section_id == "description"

    def test_returns_failure_when_previous_validation_is_valid(self) -> None:
        original_context = create_paragraph()
        translated_context = create_paragraph("translated")

        strategy = paragraph_translation_strategy

        current_validation = create_validation_result(
            issues=(
                create_validation_issue(
                    repair_instruction="Fix current validation.",
                ),
            )
        )
        previous_validation = create_validation_result()

        result = merge_retry_context(
            section_id="description",
            section_definition=create_section_translation(),
            content_strategy=strategy,
            current_validation=current_validation,
            previous_validation=previous_validation,
            original_context=original_context,
            translated_context=translated_context,
        )

        assert isinstance(result, Failure)

        error = result.failure()

        assert isinstance(error, TranslationError)
        assert error.phase == "retry-context"
        assert error.content_type == original_context.kind
        assert error.section_id == "description"

    def test_returns_retry_context_from_updater(
        self,
        mocker: MockerFixture,
    ) -> None:
        original_context = create_paragraph()
        translated_context = create_paragraph("translated")

        strategy = paragraph_translation_strategy

        current_validation = create_validation_result(
            issues=(
                create_validation_issue(
                    code="invalid-content",
                    repair_instruction="Fix the translation.",
                ),
            )
        )
        previous_validation = create_validation_result(
            issues=(
                create_validation_issue(
                    code="previous-invalid",
                    repair_instruction="Fix the previous translation.",
                ),
            )
        )

        expected_context = create_paragraph(
            "translated with retry context",
        )
        expected_state = TranslationState[Paragraph](
            context=expected_context,
            validation=current_validation,
        )

        retry_context_updater = mocker.patch.object(
            strategy,
            "retry_context_updater",
            return_value=Success(expected_state),
        )

        section_definition = create_section_translation()

        result = merge_retry_context(
            section_id="description",
            section_definition=section_definition,
            content_strategy=strategy,
            current_validation=current_validation,
            previous_validation=previous_validation,
            original_context=original_context,
            translated_context=translated_context,
        )

        assert isinstance(result, Success)
        assert result.unwrap() is expected_state

        retry_context_updater.assert_called_once()

        retry_arg = retry_context_updater.call_args.args[0]

        assert isinstance(retry_arg, RetryContextArg)
        assert retry_arg.section_id == "description"
        assert retry_arg.section_definition is section_definition
        assert retry_arg.current_validation is current_validation
        assert retry_arg.previous_validation is previous_validation
        assert retry_arg.original_context is original_context
        assert retry_arg.translated_context is translated_context

    def test_returns_failure_from_retry_context_updater(
        self,
        mocker: MockerFixture,
    ) -> None:
        original_context = create_paragraph()
        translated_context = create_paragraph("translated")

        strategy = paragraph_translation_strategy

        current_validation = create_validation_result(
            issues=(create_validation_issue(),)
        )

        error = TranslationError(
            "failed to build retry context",
            content_type=original_context.kind,
            phase="retry-context",
            section_id="description",
        )

        mocker.patch.object(
            strategy,
            "retry_context_updater",
            return_value=Failure(error),
        )

        result = merge_retry_context(
            section_id="description",
            section_definition=create_section_translation(),
            content_strategy=strategy,
            current_validation=current_validation,
            previous_validation=None,
            original_context=original_context,
            translated_context=translated_context,
        )

        assert isinstance(result, Failure)
        assert result.failure() is error
