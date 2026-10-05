from gyomu_ai_compiler.pipelines.readme.renderer.section import (
    README_SECTION_PROMPT_MAP,
)
from gyomu_schema.conversation.conversation import ConversationSchema
from gyomu_schema.error.io import GyomuIOError
from gyomu_schema.schemas.concept.base import DocumentBaseContext
from gyomu_schema.schemas.concept.readme.types import ReadmeSectionId
from gyomu_schema.schemas.document.section import SectionPromptProvider
from returns.result import Result


def _render(
    section_id: ReadmeSectionId, context: DocumentBaseContext
) -> Result[ConversationSchema, GyomuIOError]:
    return README_SECTION_PROMPT_MAP[section_id](context)


readme_prompt_provider = SectionPromptProvider[ReadmeSectionId, DocumentBaseContext](
    render=_render
)
