from gyomu_concept.document.render.markdown import render_markdown
from gyomu_concept.document.translation.document import TranslatedDocument
from gyomu_concept.readme.internal.filename import get_readme_filename
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.base import DocumentBaseContext
from gyomu_schema.schemas.concept.readme.types import (
    README_LINK,
    README_SECTION_TITLES,
    ReadmeSectionId,
)
from gyomu_schema.schemas.document.section import LanguageCodes, Section


def _get_title(context: DocumentBaseContext) -> str:
    return context.knowledge.package.display_name


def _get_section_title(
    language: LanguageCodes, section: Section[ReadmeSectionId]
) -> str:
    if section.title is not None:
        return section.title
    return README_SECTION_TITLES[language][section.id]


def _get_language_link(
    language: LanguageCodes, plan: TranslatedDocument[ReadmeSectionId]
) -> str:
    if language == plan.language:
        return README_LINK[language]
    return f"[{README_LINK[language]}]({get_readme_filename(language)})"


def render_readme_markdown(
    context: DocumentBaseContext,
    plan: TranslatedDocument[ReadmeSectionId],
    option: ConceptOption | None = None,
    need_link: bool = False,
) -> str:
    return render_markdown(
        context=context,
        plan=plan,
        get_title=_get_title,
        get_section_title=_get_section_title,
        get_language_link=_get_language_link if need_link else None,
    )
