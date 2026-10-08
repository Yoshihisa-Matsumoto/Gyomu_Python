from collections.abc import Callable

from gyomu_schema.schemas.concept.base import Knowledge
from gyomu_schema.schemas.document.content import (
    BulletList,
    BulletListItem,
    CodeBlock,
    DocumentContent,
    DocumentContentType,
    Table,
)
from gyomu_schema.schemas.document.section import (
    SUPPORTED_TRANSLATION_LANGUAGES,
    LanguageCodes,
    Section,
)

from gyomu_concept.document.translation.document import TranslatedDocument


def render_markdown[TSectionId: str, TKnowledge: Knowledge, TContext](
    context: TContext,
    plan: TranslatedDocument[TSectionId],
    get_title: Callable[[TContext], str],
    get_section_title: Callable[[LanguageCodes, Section[TSectionId]], str],
    get_language_link: Callable[[LanguageCodes, TranslatedDocument[TSectionId]], str]
    | None = None,
) -> str:
    """Renders a translated document as markdown."""

    title = f"# {get_title(context)}"

    link = ""
    if get_language_link is not None:
        link = f"{_render_link(plan, get_language_link)}\n\n"

    sections = "\n\n".join(
        _render_section(plan.language, section, get_section_title)
        for section in plan.sections
    )

    return f"{title}\n\n{link}{sections}"


def _render_link[TSectionId: str](
    plan: TranslatedDocument[TSectionId],
    get_language_link: Callable[[LanguageCodes, TranslatedDocument[TSectionId]], str],
) -> str:
    """Renders language links for a translated document."""

    return " | ".join(
        get_language_link(language, plan)
        for language in SUPPORTED_TRANSLATION_LANGUAGES
    )


def _render_section[TSectionId: str](
    language: LanguageCodes,
    section: Section[TSectionId],
    get_section_title: Callable[[LanguageCodes, Section[TSectionId]], str],
) -> str:
    """Renders a document section into markdown."""

    title = f"## {get_section_title(language, section)}"

    body = "\n\n".join(_render_content(content) for content in section.contents)

    return f"{title}\n\n{body}"


def _render_content(content: DocumentContent) -> str:
    """Renders document content based on its content kind."""

    match content.kind:
        case DocumentContentType.PARAGRAPH:
            return content.text
        case DocumentContentType.CODE:
            return _render_code_block(content)
        case DocumentContentType.BULLET_LIST:
            return _render_bullet_list(content)
        case DocumentContentType.TABLE:
            return _render_table(content)


def _render_code_block(code_block: CodeBlock) -> str:
    """Renders a code block into markdown."""

    prefix = f"### {code_block.title}\n\n" if code_block.title else ""

    return f"{prefix}```{code_block.language}\n{code_block.code}\n```"


def _render_bullet_list(bullet_list: BulletList) -> str:
    """Renders a bullet list into markdown."""

    return "\n".join(_render_bullet_list_item(item, 0) for item in bullet_list.items)


def _render_bullet_list_item(
    item: BulletListItem,
    level: int,
) -> str:
    """Renders a bullet list item and its children recursively."""

    prefix = "  " * level + "- "

    children = ""
    if item.children is not None:
        children = "\n".join(
            _render_bullet_list_item(child, level + 1) for child in item.children
        )

    return f"{prefix}{item.text}" + (f"\n{children}" if children else "")


def _render_table(table: Table) -> str:
    """Renders a table into markdown."""

    header = "| " + " | ".join(table.header.cells) + " |"
    header_span = (
        "| " + " | ".join("-" * len(cell) for cell in table.header.cells) + " |"
    )
    body = "\n".join("| " + " | ".join(row.cells) + " |" for row in table.rows)

    return f"{header}\n{header_span}\n{body}"
