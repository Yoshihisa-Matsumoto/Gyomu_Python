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
    """Represents a logical section of a document."""

    id: TSectionId = Field(
        description=(
            "Stable identifier used by renderers and translators. "
            "It should not depend on the display language."
        )
    )
    """Stable identifier used by renderers and translators."""

    title: str | None = Field(
        description=(
            "Optional section title. Omit this field entirely when no title is needed. "
            "Never use null. "
            "If omitted, the renderer may determine the title from the section id."
        ),
        default=None,
    )
    """Optional section title."""

    contents: tuple[DocumentContent, ...] = Field(
        description="Content blocks contained in the section."
    )
    """Content blocks contained in the section."""

    model_config = ConfigDict(
        json_schema_extra={
            "description": ("A logical section of a document."),
        },
    )


class TranslationState[T: DocumentContent](BaseModel):
    """Represents the translation state containing context and validation results."""

    context: T
    """The translation context content."""

    validation: ValidationResult
    """Validation result associated with the translation state."""


@dataclass
class ReconciliationValidator[T: DocumentContent]:
    """Validator for reconciling document content."""

    validate: Callable[[T, T], ValidationResult]
    """Validation function callable."""


@dataclass(frozen=True)
class DocumentContentDefinitionBase[T: DocumentContent]:
    """Base definition for document content types and translation instructions."""

    kind: DocumentContentType
    """Content type identifier."""

    content_schema: type[T]
    """Schema type for the content."""

    reconciliation: ReconciliationValidator[T]
    """Reconciliation validator for the content."""

    translation_instruction: str
    """Translation instruction string."""


@dataclass
class RetryContextArg[T: DocumentContent]:
    """Arguments provided to retry context updater."""

    section_id: str
    """Section identifier."""

    section_definition: SectionTranslationDefinition
    """Section translation definition."""

    current_validation: ValidationResult
    """Current validation result."""

    previous_validation: ValidationResult | None
    """Previous validation result if any."""

    original_context: T
    """Original content context."""

    translated_context: T
    """Translated content context."""


@dataclass
class DocumentContentTranslationStrategy[T: DocumentContent]:
    """Translation strategy for document content."""

    definition: DocumentContentDefinitionBase[T]
    """Content definition base."""

    retry_context_updater: Callable[
        [RetryContextArg[T]], Result[TranslationState[T], TranslationError]
    ]
    """Callable for updating retry context."""


@dataclass
class SectionNoTranslation:
    """Indicates that a section should not be translated."""

    strategy: Literal["none"] = "none"
    """Translation strategy literal set to none."""


@dataclass
class SectionTranslationInstruction:
    """Instructions and strategies for translating a section."""

    translation_strategies: tuple[DocumentContentTranslationStrategy[Any], ...]
    """Tuple of document content translation strategies."""

    strategy: Literal["translate"] = "translate"
    """Translation strategy literal set to translate."""

    translation_instruction: str | None = None
    """Optional translation instruction."""


type SectionTranslationDefinition = Annotated[
    SectionNoTranslation | SectionTranslationInstruction,
    Field(discriminator="strategy"),
]
"""Type alias for section translation definition."""


class SectionWithInstruction[TSectionId: str](BaseModel):
    """Section paired with an optional translation instruction."""

    section: Section[TSectionId]
    """The underlying section."""

    translation_instruction: str | None = None
    """Optional translation instruction string."""


@dataclass
class BuiltSection[TSectionId: str]:
    """Represents a built section containing both the section and its translation
    definition.
    """

    section: Section[TSectionId]
    """The built section instance."""

    translation: SectionTranslationDefinition
    """Section translation definition."""


class SectionLocation(BaseModel):
    """Location information used to identify the exact position of a translation
    target within a section.
    """

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
    """Identifier of the section containing the translation target."""

    path: tuple[str | int, ...] = Field(
        description=(
            "Path to the target value inside the section. "
            "Each element represents an object key or array index."
        ),
    )
    """Path to the target value inside the section."""


class TranslationTarget(BaseModel):
    """A text fragment extracted from a section that requires translation."""

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
    """Unique identifier of the translation target."""

    source: str = Field(
        description="Original text before translation.",
    )
    """Original text before translation."""

    location: SectionLocation = Field(
        description="Location where the translated text should be applied.",
    )
    """Location where the translated text should be applied."""


class TranslationResult(BaseModel):
    """Translation output associated with a translation target."""

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
    """Identifier of the translation target corresponding to the translated text."""

    translation: str = Field(
        description="Translated text generated for the target language.",
    )
    """Translated text generated for the target language."""


LanguageCodes = Literal["en", "ja"]
"""Literal type representing supported language codes."""

SUPPORTED_TRANSLATION_LANGUAGES: tuple[LanguageCodes, ...] = get_args(LanguageCodes)
"""Tuple of supported translation language codes."""


class TranslationRequestItem(BaseModel):
    """Represents an individual item in a translation request."""

    id: str = Field(
        description="Stable translation target identifier. Must not be changed.",
    )
    """Stable translation target identifier."""

    source: str = Field(
        description="Original text to translate.",
    )
    """Original text to translate."""


class TranslationRequest(BaseModel):
    """Represents a request for translating document items."""

    target_language: LanguageCodes = Field(
        description="Target language code for translation. Example: ja, en.",
    )
    """Target language code for translation."""

    translations: tuple[TranslationRequestItem, ...]
    """Tuple of translation request items."""


@dataclass
class SectionPromptProvider[TSectionId: str, TContext: BaseModel]:
    """Provider for rendering section prompts."""

    render: Callable[[TSectionId, TContext], Result[ConversationSchema, GyomuIOError]]
    """Render callable for section prompts."""
