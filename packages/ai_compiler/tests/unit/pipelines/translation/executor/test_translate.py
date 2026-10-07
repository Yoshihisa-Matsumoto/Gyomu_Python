from unittest.mock import AsyncMock

import pytest
from gyomu_ai.execution.parameter import GenerateObjectParams
from gyomu_ai.model.ai_model import AiModelKey
from gyomu_ai.provider.pydantic_ai.route_service import PydanticAiRoutingExecution
from gyomu_ai_compiler.pipelines.translation.executor.translate import (
    translate_document_content,
)
from gyomu_schema.error.ai import (
    AiError,
    AiErrorPhase,
    AiFailResolution,
    AiOperation,
)
from gyomu_schema.error.translation import TranslationError
from gyomu_schema.schemas.document.content import Paragraph
from gyomu_schema.schemas.document.section import DocumentContentTranslationStrategy
from gyomu_schema.schemas.document.translation.paragraph import (
    paragraph_translation_strategy,
)
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.schema.schema_test_support.concept_helpers import (
    create_paragraph,
    create_section_translation,
)


class TestTranslateDocumentContent:
    @pytest.fixture
    def context(self) -> Paragraph:
        return create_paragraph()

    @pytest.fixture
    def strategy(self) -> DocumentContentTranslationStrategy[Paragraph]:
        return paragraph_translation_strategy

    @pytest.fixture
    def section_definition(self):
        return create_section_translation()

    @pytest.mark.asyncio
    async def test_returns_prompt_failure(
        self,
        mocker: MockerFixture,
        context: Paragraph,
        strategy: DocumentContentTranslationStrategy[Paragraph],
        section_definition,
    ) -> None:
        error = TranslationError(
            "fail to build prompt message",
            content_type=context.kind,
            phase="prompt",
            section_id="description",
        )

        mocker.patch(
            "gyomu_ai_compiler.pipelines.translation.executor.translate"
            ".build_translation_prompt",
            return_value=Failure(error),
        )

        execution = mocker.patch(
            "gyomu_ai_compiler.pipelines.translation.executor.translate"
            ".PydanticAiRoutingExecution",
        )

        result = await translate_document_content(
            language="ja",
            section_id="description",
            context=context,
            section_definition=section_definition,
            content_strategy=strategy,
            validation_result=None,
        )

        assert isinstance(result, Failure)
        assert result.failure() is error
        execution.assert_not_called()

    @pytest.mark.asyncio
    async def test_returns_translation_error_when_ai_fails(
        self,
        mocker: MockerFixture,
        context: Paragraph,
        strategy: DocumentContentTranslationStrategy[Paragraph],
        section_definition,
    ) -> None:
        ai_error = AiError(
            "Failed to generate object.",
            operation=AiOperation.GENERATE,
            model_key=AiModelKey.FAST,
            model=None,
            phase=AiErrorPhase.REQUEST,
            resolution=AiFailResolution(),
        )

        execution = mocker.Mock(spec=PydanticAiRoutingExecution)
        execution.generate_object = AsyncMock(
            return_value=Failure(ai_error),
        )

        mocker.patch(
            "gyomu_ai_compiler.pipelines.translation.executor.translate"
            ".build_translation_prompt",
            return_value=Success("translation prompt"),
        )

        mocker.patch(
            "gyomu_ai_compiler.pipelines.translation.executor.translate"
            ".PydanticAiRoutingExecution",
            return_value=execution,
        )

        result = await translate_document_content(
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
        assert error.phase == "translate"
        assert error.content_type == context.kind
        assert error.section_id == "description"
        assert error.__cause__ is ai_error

        execution.generate_object.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_returns_translated_context(
        self,
        mocker: MockerFixture,
        context: Paragraph,
        strategy: DocumentContentTranslationStrategy[Paragraph],
        section_definition,
    ) -> None:
        translated_context = create_paragraph(
            text="これはペンです",
        )

        response = mocker.Mock()
        response.output = translated_context

        execution = mocker.Mock(spec=PydanticAiRoutingExecution)
        execution.generate_object = AsyncMock(
            return_value=Success(response),
        )

        mocker.patch(
            "gyomu_ai_compiler.pipelines.translation.executor.translate"
            ".build_translation_prompt",
            return_value=Success("translation prompt"),
        )

        mocker.patch(
            "gyomu_ai_compiler.pipelines.translation.executor.translate"
            ".PydanticAiRoutingExecution",
            return_value=execution,
        )

        result = await translate_document_content(
            language="ja",
            section_id="description",
            context=context,
            section_definition=section_definition,
            content_strategy=strategy,
            validation_result=None,
        )

        assert isinstance(result, Success)
        assert result.unwrap() is translated_context

    @pytest.mark.asyncio
    async def test_passes_prompt_and_parameters_to_execution(
        self,
        mocker: MockerFixture,
        context: Paragraph,
        strategy: DocumentContentTranslationStrategy[Paragraph],
        section_definition,
    ) -> None:
        translated_context = create_paragraph(
            text="これはペンです",
        )

        response = mocker.Mock()
        response.output = translated_context

        execution = mocker.Mock(spec=PydanticAiRoutingExecution)
        execution.generate_object = AsyncMock(
            return_value=Success(response),
        )

        mocker.patch(
            "gyomu_ai_compiler.pipelines.translation.executor.translate"
            ".build_translation_prompt",
            return_value=Success("translation prompt"),
        )

        mocker.patch(
            "gyomu_ai_compiler.pipelines.translation.executor.translate"
            ".PydanticAiRoutingExecution",
            return_value=execution,
        )

        await translate_document_content(
            language="ja",
            section_id="description",
            context=context,
            section_definition=section_definition,
            content_strategy=strategy,
            validation_result=None,
        )

        execution.generate_object.assert_awaited_once()

        assert execution.generate_object.await_args

        conversation, params = execution.generate_object.await_args.args

        assert conversation.request is not None
        assert conversation.request.parts[0].text == "translation prompt"

        assert isinstance(params, GenerateObjectParams)
        assert params.key is AiModelKey.FAST
        assert params.output_type is strategy.definition.content_schema
