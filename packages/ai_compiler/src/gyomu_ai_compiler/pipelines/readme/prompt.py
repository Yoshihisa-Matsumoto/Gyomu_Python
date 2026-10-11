from gyomu_schema.conversation.conversation import ConversationSchema
from gyomu_schema.error.io import GyomuIOError
from gyomu_schema.schemas.concept.base import DocumentBaseContext, Knowledge
from gyomu_schema.schemas.concept.readme.types import ReadmeSectionId
from gyomu_schema.schemas.document.section import SectionPromptProvider
from returns.result import Result

from gyomu_ai_compiler.pipelines.readme.renderer.section import (
    README_SECTION_PROMPT_MAP,
)


def _render(
    section_id: ReadmeSectionId, context: DocumentBaseContext[Knowledge]
) -> Result[ConversationSchema, GyomuIOError]:
    """Render a README section prompt based on the provided section ID and context.

    Renders the appropriate prompt conversation schema for a given README section and
    document context.

    Args:
        section_id (ReadmeSectionId): The section identifier for the README.
        context (DocumentBaseContext): The document base context providing data for the
            prompt.

    Returns:
        Result[ConversationSchema, GyomuIOError]: A Result containing the rendered
            ConversationSchema or a GyomuIOError.
    """
    return README_SECTION_PROMPT_MAP[section_id](context)


readme_prompt_provider = SectionPromptProvider[
    ReadmeSectionId, DocumentBaseContext[Knowledge]
](render=_render)
"""Section prompt provider for README generation.

Section prompt provider configured for README generation using section identifiers and
document contexts.
"""
