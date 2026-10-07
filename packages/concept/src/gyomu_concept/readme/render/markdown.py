from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.base import DocumentBaseContext
from gyomu_schema.schemas.concept.readme.types import (
    README_LINK,
    README_SECTION_TITLES,
    ReadmeSectionId,
)
from gyomu_schema.schemas.document.section import LanguageCodes, Section

from gyomu_concept.document.render.markdown import render_markdown
from gyomu_concept.document.translation.document import TranslatedDocument
from gyomu_concept.readme.internal.filename import get_readme_filename


def _get_title(context: DocumentBaseContext) -> str:
    """Get the document title from the package knowledge.

    Get the document title from the package display name.

    Args:
        context (DocumentBaseContext): The document base context containing knowledge
            and package details.

    Returns:
        str: The package display name.
    """
    return context.knowledge.package.display_name


def _get_section_title(
    language: LanguageCodes, section: Section[ReadmeSectionId]
) -> str:
    """Get the section title for the given language and section.

    Get the title for a section, falling back to the default localized README section
    title if none is specified.

    Args:
        language (LanguageCodes): The target language code.
        section (Section[ReadmeSectionId]): The section object containing the title and
            ID.

    Returns:
        str: The resolved section title.
    """
    if section.title is not None:
        return section.title
    return README_SECTION_TITLES[language][section.id]


def _get_language_link(
    language: LanguageCodes, plan: TranslatedDocument[ReadmeSectionId]
) -> str:
    """Get the markdown link or label for a language.

    Get the markdown link representation for a language, returning a plain label if it
    is the current language or a markdown link otherwise.

    Args:
        language (LanguageCodes): The target language code.
        plan (TranslatedDocument[ReadmeSectionId]): The translated document plan.

    Returns:
        str: The formatted language link or label string.
    """
    if language == plan.language:
        return README_LINK[language]
    return f"[{README_LINK[language]}]({get_readme_filename(language)})"


def render_readme_markdown(
    context: DocumentBaseContext,
    plan: TranslatedDocument[ReadmeSectionId],
    option: ConceptOption | None = None,
    need_link: bool = False,
) -> str:
    """Render the README document as Markdown.

    Render the README document in Markdown format based on the given context and
    translation plan.

    Args:
        context (DocumentBaseContext): The document base context.
        plan (TranslatedDocument[ReadmeSectionId]): The translated README document plan.
        option (ConceptOption | None): Optional concept generation options.
        need_link (bool): Whether to include language navigation links.

    Returns:
        str: The rendered README markdown content.
    """
    return render_markdown(
        context=context,
        plan=plan,
        get_title=_get_title,
        get_section_title=_get_section_title,
        get_language_link=_get_language_link if need_link else None,
    )
