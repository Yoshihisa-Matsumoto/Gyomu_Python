from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.llm_context.input import LlmContextBuildContext
from gyomu_schema.schemas.concept.llm_context.types import (
    LLM_CONTEXT_SECTION_TITLES,
    LlmContextSectionId,
)
from gyomu_schema.schemas.document.section import LanguageCodes, Section

from gyomu_concept.document.render.markdown import render_markdown
from gyomu_concept.document.translation.document import TranslatedDocument


def _get_title(context: LlmContextBuildContext) -> str:
    """Get the display name of the package as the title.

    Returns:
        str: The display name of the package.
    """
    return context.knowledge.package.display_name


def _get_section_title(
    language: LanguageCodes, section: Section[LlmContextSectionId]
) -> str:
    """Get the title for a given section, falling back to default localized titles if
    not specified.

    Returns:
        str: The section title string.
    """
    if section.title is not None:
        return section.title
    return LLM_CONTEXT_SECTION_TITLES[language][section.id]


def render_llm_context_markdown(
    context: LlmContextBuildContext,
    plan: TranslatedDocument[LlmContextSectionId],
    option: ConceptOption | None = None,
    need_link: bool = False,
) -> str:
    """Render the LLM context into a markdown-formatted string.

    Returns:
        str: The rendered markdown string.
    """
    return render_markdown(
        context=context,
        plan=plan,
        get_title=_get_title,
        get_section_title=_get_section_title,
        get_language_link=None,
    )
