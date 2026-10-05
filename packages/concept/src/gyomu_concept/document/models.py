from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal, Never

from gyomu_concept.document.builder.section import SectionBuilder
from gyomu_concept.document.translation.document import TranslatedDocument
from gyomu_concept.error.document import DocumentBuilderError
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.base import DocumentBaseContext
from gyomu_schema.schemas.document.section import LanguageCodes
from gyomu_schema.schemas.types import FullPath
from returns.result import Result


@dataclass
class TextRenderedDocument:
    content: str
    type: Literal["text"] = "text"


@dataclass
class BinaryRenderedDocument:
    content: bytes
    type: Literal["binary"] = "binary"


type RendererdDocument = TextRenderedDocument | BinaryRenderedDocument


@dataclass
class FilepathResolver:
    resolve: Callable[[ProjectContext, LanguageCodes], FullPath]


@dataclass
class DocumentRenderer[
    TSectionId: str,
    TContext: DocumentBaseContext,
    TOption: ConceptOption,
    TRendererOption,
]:
    render: Callable[
        [
            TContext,
            TranslatedDocument[TSectionId],
            TOption | None,
            TRendererOption | None,
        ],
        Result[RendererdDocument, DocumentBuilderError],
    ]


@dataclass
class DocumentOutput[
    TSectionId: str,
    TContext: DocumentBaseContext,
    TOption: ConceptOption,
    TRendererOption,
]:
    renderer: DocumentRenderer[TSectionId, TContext, TOption, TRendererOption]
    filepath_resolver: FilepathResolver


@dataclass
class DocumentDefinition[
    TSectionId: str,
    TContext: DocumentBaseContext,
    TOption: ConceptOption,
    TRendererOption = Never,
]:
    create_context: Callable[
        [ProjectContext, TOption | None], Result[TContext, DocumentBuilderError]
    ]

    supported_languages: tuple[LanguageCodes, ...]

    section_builders: tuple[SectionBuilder[TSectionId, TContext], ...]

    output: DocumentOutput[TSectionId, TContext, TOption, TRendererOption]

    renderer_options: TRendererOption | None

    is_scope_of_debug: Callable[[TOption], bool]

    log_prefix: str
