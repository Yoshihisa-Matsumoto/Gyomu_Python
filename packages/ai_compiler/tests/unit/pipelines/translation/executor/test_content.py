from unittest.mock import AsyncMock, Mock

import pytest
from gyomu_ai_compiler.pipelines.translation.executor.content import (
    execute_document_content_translation,
)
from gyomu_schema.error.translation import TranslationError
from gyomu_schema.schemas.document.section import (
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


class TestExecuteDocumentContentTranslation:
    @pytest.mark.asyncio
    async def test_returns_translation_failure(
        self,
        mocker: MockerFixture,
    ) -> None:
        context = create_paragraph()

        error = TranslationError(
            "fail to translate",
            content_type=context.kind,
            phase="translate",
            section_id="description",
        )

        mocker.patch(
            "gyomu_ai_compiler.pipelines.translation.executor.content"
            ".translate_document_content",
            new_callable=AsyncMock,
            return_value=Failure(error),
        )

        result = await execute_document_content_translation(
            language="ja",
            section_id="description",
            context=context,
            section_definition=create_section_translation(),
            content_strategy=Mock(),
        )

        assert isinstance(result, Failure)
        assert result.failure() is error

    @pytest.mark.asyncio
    async def test_returns_translated_context_when_first_translation_is_valid(
        self,
        mocker: MockerFixture,
    ) -> None:
        context = create_paragraph()
        translated_context = create_paragraph("これはペンです")

        strategy = paragraph_translation_strategy

        mocker.patch(
            "gyomu_ai_compiler.pipelines.translation.executor.content"
            ".translate_document_content",
            new_callable=AsyncMock,
            return_value=Success(translated_context),
        )

        merge = mocker.patch(
            "gyomu_ai_compiler.pipelines.translation.executor.content"
            ".merge_retry_context",
        )

        result = await execute_document_content_translation(
            language="ja",
            section_id="description",
            context=context,
            section_definition=create_section_translation(),
            content_strategy=strategy,
        )

        assert isinstance(result, Success)
        assert result.unwrap() is translated_context

        merge.assert_not_called()

    @pytest.mark.asyncio
    async def test_retries_when_validation_fails_and_returns_second_translation(
        self,
        mocker: MockerFixture,
    ) -> None:
        context = create_paragraph("this is a pen")
        retry_context = create_paragraph("retry context")
        first_translation = create_paragraph("first translation")
        second_translation = create_paragraph("これはペンです")

        invalid_validation = create_validation_result(
            issues=(
                create_validation_issue(
                    repair_instruction="Fix the translation.",
                ),
            )
        )
        valid_validation = create_validation_result()

        strategy = paragraph_translation_strategy
        mocker.patch.object(
            strategy.definition.reconciliation,
            "validate",
            side_effect=[
                invalid_validation,
                valid_validation,
            ],
        )

        translate = mocker.patch(
            "gyomu_ai_compiler.pipelines.translation.executor.content"
            ".translate_document_content",
            new_callable=AsyncMock,
            side_effect=[
                Success(first_translation),
                Success(second_translation),
            ],
        )

        merge = mocker.patch(
            "gyomu_ai_compiler.pipelines.translation.executor.content"
            ".merge_retry_context",
            return_value=Success(
                TranslationState(
                    context=retry_context,
                    validation=invalid_validation,
                )
            ),
        )

        result = await execute_document_content_translation(
            language="ja",
            section_id="description",
            context=context,
            section_definition=create_section_translation(),
            content_strategy=strategy,
        )

        assert isinstance(result, Success)
        assert result.unwrap() is second_translation

        assert translate.await_count == 2

        first_call = translate.await_args_list[0]
        second_call = translate.await_args_list[1]

        assert first_call.args[2] is context
        assert second_call.args[2] is retry_context

        assert first_call.args[5] is None
        assert second_call.args[5] is invalid_validation

        merge.assert_awaited_once() if hasattr(merge, "assert_awaited_once") else None

    @pytest.mark.asyncio
    async def test_returns_merge_failure(
        self,
        mocker: MockerFixture,
    ) -> None:
        context = create_paragraph()
        translated_context = create_paragraph("translated")

        invalid_validation = create_validation_result(
            issues=(create_validation_issue(),)
        )

        merge_error = TranslationError(
            "failed to build retry context",
            content_type=context.kind,
            phase="retry-context",
            section_id="description",
        )

        strategy = paragraph_translation_strategy
        mocker.patch.object(
            strategy.definition.reconciliation,
            "validate",
            return_value=invalid_validation,
        )
        mocker.patch(
            "gyomu_ai_compiler.pipelines.translation.executor.content"
            ".translate_document_content",
            new_callable=AsyncMock,
            return_value=Success(translated_context),
        )

        mocker.patch(
            "gyomu_ai_compiler.pipelines.translation.executor.content"
            ".merge_retry_context",
            return_value=Failure(merge_error),
        )

        result = await execute_document_content_translation(
            language="ja",
            section_id="description",
            context=context,
            section_definition=create_section_translation(),
            content_strategy=strategy,
        )

        assert isinstance(result, Failure)
        assert result.failure() is merge_error

    @pytest.mark.asyncio
    async def test_returns_failure_after_max_translation_attempts(
        self,
        mocker: MockerFixture,
    ) -> None:
        context = create_paragraph()

        invalid_validation = create_validation_result(
            issues=(create_validation_issue(),)
        )

        strategy = paragraph_translation_strategy
        mocker.patch.object(
            strategy.definition.reconciliation,
            "validate",
            return_value=invalid_validation,
        )

        mocker.patch(
            "gyomu_ai_compiler.pipelines.translation.executor.content"
            ".translate_document_content",
            new_callable=AsyncMock,
            return_value=Success(context),
        )

        mocker.patch(
            "gyomu_ai_compiler.pipelines.translation.executor.content"
            ".merge_retry_context",
            return_value=Success(
                TranslationState(
                    context=context,
                    validation=invalid_validation,
                )
            ),
        )

        result = await execute_document_content_translation(
            language="ja",
            section_id="description",
            context=context,
            section_definition=create_section_translation(),
            content_strategy=strategy,
        )

        assert isinstance(result, Failure)

        error = result.failure()

        assert isinstance(error, TranslationError)
        assert error.phase == "retry"
        assert error.content_type == context.kind
        assert error.section_id == "description"
