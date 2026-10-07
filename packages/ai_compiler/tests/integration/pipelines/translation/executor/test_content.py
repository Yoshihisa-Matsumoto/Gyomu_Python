from pathlib import Path

import gyomu_ai_compiler.pipelines.translation.executor.content as content_module
import pytest
from gyomu_ai_compiler.pipelines.document import DocumentRouteId
from gyomu_ai_compiler.pipelines.translation.executor.content import (
    execute_document_content_translation,
)
from gyomu_infra.logger import logger
from gyomu_schema.error.config import ConfigError
from gyomu_schema.schemas.document.section import SectionTranslationInstruction
from gyomu_schema.schemas.document.translation.paragraph import (
    paragraph_translation_strategy,
)
from pytest_mock import MockerFixture
from returns.result import Success

from packages.ai.ai_test_support.helper import register_test_google_routing
from packages.schema.schema_test_support.concept_helpers import create_paragraph


@pytest.mark.asyncio
async def test_returns_translated_context_when_first_translation_is_valid(
    project_dot_env: Path,
    mocker: MockerFixture,
) -> None:
    try:
        register_test_google_routing(project_dot_env, [DocumentRouteId])
    except ConfigError:
        pytest.skip("GEMINI_API_KEY is not configured")

    spy = mocker.spy(content_module, "translate_document_content")

    context = create_paragraph(
        text=(
            "Contributors must strictly maintain the "
            "separation between the structural "
            "knowledge model and its final output "
            "formats. Because the Concept functions as "
            "a format-agnostic model combining source "
            "code analysis and human-managed "
            "Knowledge, contributors must ensure that "
            "the core data structures remain "
            "independent of specific document formats "
            "or output languages. When implementing "
            "changes to package or directory concepts, "
            "developers are required to preserve the "
            "distinct boundaries between source code "
            "analysis, Concept construction, and "
            "documentation generation, ensuring that "
            "these operations never tightly couple "
            "with one another.\n"
            "\n"
            "All interactions involving AI must be "
            "routed exclusively through "
            "`gyomu-ai-compiler` to prevent direct "
            "dependencies on specific AI providers or "
            "models. Contributors introducing "
            "document-specific configurations—such as "
            "translation instructions for document "
            "content—must encapsulate these "
            "definitions directly within the Concept "
            "layer rather than embedding them into "
            "execution scripts. When extending README "
            "generation or coordinating section "
            "builders, developers must treat Concept "
            "and Knowledge as the sole inputs, "
            "transforming them strictly into the "
            "requested document structures while "
            "maintaining the integrity of the shared "
            "human-AI knowledge representation."
        )
    )

    strategy = paragraph_translation_strategy

    result = await execute_document_content_translation(
        language="ja",
        section_id="development",
        context=context,
        section_definition=SectionTranslationInstruction(translation_strategies=()),
        content_strategy=strategy,
    )

    assert isinstance(result, Success)
    logger.debug(result.unwrap().text)
    logger.debug(f"Count:{spy.call_count}")
