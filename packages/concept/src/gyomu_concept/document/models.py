from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal, Never

from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.document.section import LanguageCodes
from gyomu_schema.schemas.types import FullPath
from returns.result import Result

from gyomu_concept.document.builder.section import SectionBuilder
from gyomu_concept.document.translation.document import TranslatedDocument
from gyomu_concept.error.document import DocumentBuilderError


@dataclass
class TextRenderedDocument:
    """Represents a text-based rendered document."""

    content: str
    """The text content of the document."""

    type: Literal["text"] = "text"
    """The document type indicator, fixed to 'text'."""


@dataclass
class BinaryRenderedDocument:
    """Represents a binary-based rendered document."""

    content: bytes
    """The binary content of the document."""

    type: Literal["binary"] = "binary"
    """The document type indicator, fixed to 'binary'."""


type RendererdDocument = TextRenderedDocument | BinaryRenderedDocument
"""Represents a rendered document, which can be either text or binary."""


@dataclass
class FilepathResolver:
    """Resolves file paths for documents based on project context and language codes."""

    resolve: Callable[[ProjectContext, LanguageCodes], FullPath]
    """Callable that performs the filepath resolution."""


@dataclass
class DocumentRenderer[
    TSectionId: str,
    TContext,
    TOption: ConceptOption,
    TRendererOption,
]:
    """Handles the rendering of translated documents into rendered documents."""

    render: Callable[
        [
            TContext,
            TranslatedDocument[TSectionId],
            TOption | None,
            TRendererOption | None,
        ],
        Result[RendererdDocument, DocumentBuilderError],
    ]
    """Callable that renders the document."""


@dataclass
class DocumentOutput[
    TSectionId: str,
    TContext,
    TOption: ConceptOption,
    TRendererOption,
]:
    """Defines the output configuration containing a renderer and a filepath
    resolver.
    """

    renderer: DocumentRenderer[TSectionId, TContext, TOption, TRendererOption]
    """The document renderer instance."""

    filepath_resolver: FilepathResolver
    """The filepath resolver instance."""


@dataclass
class DocumentDefinition[
    TSectionId: str,
    TContext,
    TOption: ConceptOption,
    TRendererOption = Never,
]:
    """Defines the complete structure, building blocks, and output configuration for
    a document.
    """

    create_context: Callable[
        [ProjectContext, TOption | None], Result[TContext, DocumentBuilderError]
    ]
    """Callable that creates the document context."""

    supported_languages: tuple[LanguageCodes, ...]
    """Tuple of languages supported by the document."""

    section_builders: tuple[SectionBuilder[TSectionId, TContext], ...]
    """Tuple of section builders used to construct the document."""

    output: DocumentOutput[TSectionId, TContext, TOption, TRendererOption]
    """The document output configuration containing renderer and filepath resolver."""

    renderer_options: TRendererOption | None
    """Optional configuration options for the renderer."""

    is_scope_of_debug: Callable[[TOption], bool]
    """Callable that determines if debug logging applies to the given option."""

    log_prefix: str
    """Prefix string used for logging messages."""
