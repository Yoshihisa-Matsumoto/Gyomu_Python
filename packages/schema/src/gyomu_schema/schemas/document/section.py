from typing import Annotated, Literal

from gyomu_schema.schemas.document.content import DocumentContent
from gyomu_schema.schemas.document.translation import DocumentContentTranslationStrategy
from pydantic import BaseModel, ConfigDict, Field


class Section(BaseModel):
    id: str = Field(
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


class SectionNoTranslation(BaseModel):
    strategy: Literal["none"] = "none"


class SectionTranslationInstruction(BaseModel):
    strategy: Literal["translate"] = "translate"
    translation_instruction: str | None = None
    translation_strategies: tuple[DocumentContentTranslationStrategy, ...]


type SectionTranslationDefinition = Annotated[
    SectionNoTranslation | SectionTranslationInstruction,
    Field(discriminator="strategy"),
]


class SectionWithInstruction(BaseModel):
    section: Section
    translation_instruction: str | None = None


class BuiltSection(BaseModel):
    section: Section
    translation: SectionTranslationDefinition
