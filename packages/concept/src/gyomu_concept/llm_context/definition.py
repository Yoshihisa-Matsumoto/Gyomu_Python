from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.llm_context.input import LlmContextBuildContext
from gyomu_schema.schemas.concept.llm_context.types import LlmContextSectionId
from returns.result import Success

from gyomu_concept.document.models import (
    DocumentDefinition,
    DocumentOutput,
    DocumentRenderer,
    FilepathResolver,
    TextRenderedDocument,
)
from gyomu_concept.llm_context.builder.sections import LLMCONTEXT_SECTION_BUILDERS
from gyomu_concept.llm_context.context import initialize_llm_context_build_context
from gyomu_concept.llm_context.render.markdown import render_llm_context_markdown

_llm_context_markdown_renderer = DocumentRenderer[
    LlmContextSectionId,
    LlmContextBuildContext,
    ConceptOption,
    None,
](
    render=(
        lambda context, document, option, render_option: Success(
            TextRenderedDocument(
                content=render_llm_context_markdown(
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

_filepath_resolver = FilepathResolver(
    resolve=(lambda context, _: context.project_root / "Context.md")
)


def _is_scope_of_debug(option: ConceptOption) -> bool:
    return option.debug_info.llm_context_sections


LLMCONTEXT_DOCUMENT_DEFINITION = DocumentDefinition[
    LlmContextSectionId,
    LlmContextBuildContext,
    ConceptOption,
    None,
](
    create_context=initialize_llm_context_build_context,
    supported_languages=("en",),
    section_builders=LLMCONTEXT_SECTION_BUILDERS,
    renderer_options=None,
    output=DocumentOutput[
        LlmContextSectionId,
        LlmContextBuildContext,
        ConceptOption,
        None,
    ](renderer=_llm_context_markdown_renderer, filepath_resolver=_filepath_resolver),
    log_prefix="LLM-CONTEXT",
    is_scope_of_debug=_is_scope_of_debug,
)
