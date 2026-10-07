from dataclasses import dataclass

from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.base import DocumentBaseContext
from gyomu_schema.schemas.concept.readme.types import ReadmeSectionId
from returns.result import Success

from gyomu_concept.document.models import (
    DocumentDefinition,
    DocumentOutput,
    DocumentRenderer,
    FilepathResolver,
    TextRenderedDocument,
)
from gyomu_concept.readme.builder.sections import README_SECTION_BUILDERS
from gyomu_concept.readme.context import initialize_readme_build_context
from gyomu_concept.readme.internal.filename import get_readme_filename
from gyomu_concept.readme.render.markdown import render_readme_markdown


@dataclass(frozen=True)
class ReadmeMarkdownRendererOption:
    """Options for rendering the README markdown."""

    need_link: bool | None = None
    """Flag indicating whether links should be included."""


_readme_markdown_renderer = DocumentRenderer[
    ReadmeSectionId, DocumentBaseContext, ConceptOption, ReadmeMarkdownRendererOption
](
    render=(
        lambda context, document, option, render_option: Success(
            TextRenderedDocument(
                content=render_readme_markdown(
                    context,
                    document,
                    option,
                    render_option.need_link
                    if render_option is not None and render_option.need_link is not None
                    else False,
                )
            )
        )
    )
)
"""Markdown document renderer for README generation."""


_filepath_resolver = FilepathResolver(
    resolve=(
        lambda context, language: context.project_root / get_readme_filename(language)
    )
)
"""Filepath resolver for README generation based on language."""


def _is_scope_of_debug(option: ConceptOption) -> bool:
    """Checks if README sections are within the debug scope.

    Args:
        option (ConceptOption): Concept options configuration.

    Returns:
        bool: True if debug scope includes README sections, false otherwise.
    """
    return option.debug_info.readme_sections


README_DOCUMENT_DEFINITION = DocumentDefinition[
    ReadmeSectionId, DocumentBaseContext, ConceptOption, ReadmeMarkdownRendererOption
](
    create_context=initialize_readme_build_context,
    supported_languages=("en", "ja"),
    section_builders=README_SECTION_BUILDERS,
    renderer_options=ReadmeMarkdownRendererOption(need_link=True),
    output=DocumentOutput[
        ReadmeSectionId,
        DocumentBaseContext,
        ConceptOption,
        ReadmeMarkdownRendererOption,
    ](renderer=_readme_markdown_renderer, filepath_resolver=_filepath_resolver),
    log_prefix="README",
    is_scope_of_debug=_is_scope_of_debug,
)
"""Document definition for generating project README files."""
