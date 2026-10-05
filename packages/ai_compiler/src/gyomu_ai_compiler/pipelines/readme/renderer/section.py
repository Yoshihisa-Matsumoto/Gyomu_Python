from collections.abc import Callable, Mapping

from gyomu_ai_compiler.pipelines.readme.renderer.architecture import (
    build_architecture_messages,
)
from gyomu_ai_compiler.pipelines.readme.renderer.dependencies import (
    build_dependencies_messages,
)
from gyomu_ai_compiler.pipelines.readme.renderer.development import (
    build_development_messages,
)
from gyomu_ai_compiler.pipelines.readme.renderer.overview import build_overview_messages
from gyomu_schema.conversation.conversation import ConversationSchema
from gyomu_schema.error.io import GyomuIOError
from gyomu_schema.schemas.concept.base import DocumentBaseContext
from gyomu_schema.schemas.concept.readme.types import ReadmeSectionId
from returns.result import Result

README_SECTION_PROMPT_MAP: Mapping[
    ReadmeSectionId,
    Callable[[DocumentBaseContext], Result[ConversationSchema, GyomuIOError]],
] = {
    "overview": build_overview_messages,
    "architecture": build_architecture_messages,
    "dependencies": build_dependencies_messages,
    "development": build_development_messages,
}
