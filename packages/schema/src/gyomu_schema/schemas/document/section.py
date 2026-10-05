from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Annotated, Any, Literal, get_args

from pydantic import BaseModel, ConfigDict, Field
from returns.result import Result

from gyomu_schema.conversation.conversation import ConversationSchema
from gyomu_schema.error.io import GyomuIOError
from gyomu_schema.error.translation import TranslationError
from gyomu_schema.schemas.document.content import (
    DocumentContent,
    DocumentContentType,
)
from gyomu_schema.schemas.document.validation import ValidationResult


class Section[TSectionId: str](BaseModel):
    id: TSectionId = Field(
        description=(
            "Stable identifier used by renderers and translators. "
            "It should not depend on the display language."
        )
    )
    title: str | None = Field(
        description=(
            "Optional section title. Omit this field entirely when no title is needed. "
            "Never use null. "
            "If omitted, the renderer may determine the title from the section id."
        ),
        default=None,
    )
    contents: tuple[DocumentContent, ...] = Field(
        description="Content blocks contained in the section."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "description": ("A logical section of a document."),
        },
    )


class TranslationState[T: DocumentContent](BaseModel):
    context: T
    validation: ValidationResult


@dataclass
class ReconciliationValidator[T: DocumentContent]:
    validate: Callable[[T, T], ValidationResult]


@dataclass(frozen=True)
class DocumentContentDefinitionBase[T: DocumentContent]:
    kind: DocumentContentType
    content_schema: type[T]
    reconciliation: ReconciliationValidator[T]
    translation_instruction: str


@dataclass
class RetryContextArg[T: DocumentContent]:
    section_id: str
    section_definition: SectionTranslationDefinition
    current_validation: ValidationResult
    previous_validation: ValidationResult | None
    original_context: T
    translated_context: T


@dataclass
class DocumentContentTranslationStrategy[T: DocumentContent]:
    definition: DocumentContentDefinitionBase[T]

    retry_context_updater: Callable[
        [RetryContextArg[T]], Result[TranslationState[T], TranslationError]
    ]


@dataclass
class SectionNoTranslation:
    strategy: Literal["none"] = "none"


@dataclass
class SectionTranslationInstruction:
    translation_strategies: tuple[DocumentContentTranslationStrategy[Any], ...]
    strategy: Literal["translate"] = "translate"
    translation_instruction: str | None = None


type SectionTranslationDefinition = Annotated[
    SectionNoTranslation | SectionTranslationInstruction,
    Field(discriminator="strategy"),
]


class SectionWithInstruction[TSectionId: str](BaseModel):
    section: Section[TSectionId]
    translation_instruction: str | None = None


@dataclass
class BuiltSection[TSectionId: str]:
    section: Section[TSectionId]
    translation: SectionTranslationDefinition


class SectionLocation(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "description": (
                "Location information used to identify the exact position "
                "of a translation target within a README section."
            ),
        },
    )

    section_id: str = Field(
        description=(
            "Identifier of the README section containing the translation target."
        ),
    )

    path: tuple[str | int, ...] = Field(
        description=(
            "Path to the target value inside the section. "
            "Each element represents an object key or array index."
        ),
    )


class TranslationTarget(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "description": (
                "A text fragment extracted from a README section "
                "that requires translation."
            ),
        },
    )

    id: str = Field(
        description=(
            "Unique identifier of the translation target. "
            "Used to associate source text with translated text."
        ),
    )

    source: str = Field(
        description="Original text before translation.",
    )

    location: SectionLocation = Field(
        description="Location where the translated text should be applied.",
    )


class TranslationResult(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "description": ("Translation output associated with a translation target."),
        },
    )

    id: str = Field(
        description=(
            "Identifier of the translation target corresponding to the translated text."
        ),
    )

    translation: str = Field(
        description="Translated text generated for the target language.",
    )


LanguageCodes = Literal["en", "ja"]
SUPPORTED_TRANSLATION_LANGUAGES: tuple[LanguageCodes, ...] = get_args(LanguageCodes)


class TranslationRequestItem(BaseModel):
    id: str = Field(
        description="Stable translation target identifier. Must not be changed.",
    )

    source: str = Field(
        description="Original text to translate.",
    )


class TranslationRequest(BaseModel):
    target_language: LanguageCodes = Field(
        description="Target language code for translation. Example: ja, en.",
    )

    translations: tuple[TranslationRequestItem, ...]


@dataclass
class SectionPromptProvider[TSectionId: str, TContext: BaseModel]:
    render: Callable[[TSectionId, TContext], Result[ConversationSchema, GyomuIOError]]
