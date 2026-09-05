from enum import StrEnum
from typing import Literal, TypedDict

from pydantic import BaseModel

from gyomu_schema.schemas.python.location import SourceLocation


class DocstringStyle(StrEnum):
    GOOGLE = "google"


class DocstringSectionKind(StrEnum):
    ARGS = "args"
    RETURNS = "returns"
    RAISES = "raises"
    EXAMPLES = "examples"
    NOTES = "notes"
    CUSTOM = "custom"
    GYOMU_CONTEXT = "gyomu_context"
    TEXT = "text"


class DocstringTextSection(BaseModel):
    kind: Literal[DocstringSectionKind.TEXT] = DocstringSectionKind.TEXT
    value: str


class DocstringParametersSectionItem(BaseModel):
    name: str
    type: str | None
    description: str


class DocstringParametersSection(BaseModel):
    kind: Literal[DocstringSectionKind.ARGS] = DocstringSectionKind.ARGS
    items: tuple[DocstringParametersSectionItem, ...]


class DocstringReturnsSectionItem(BaseModel):
    type: str | None
    description: str


class DocstringReturnsSection(BaseModel):
    kind: Literal[DocstringSectionKind.RETURNS] = DocstringSectionKind.RETURNS
    item: DocstringReturnsSectionItem


class DocstringRaisesSectionItem(BaseModel):
    type: str | None
    description: str


class DocstringRaisesSection(BaseModel):
    kind: Literal[DocstringSectionKind.RAISES] = DocstringSectionKind.RAISES
    items: tuple[DocstringRaisesSectionItem, ...]


class DocstringExamplesSectionItem(BaseModel):
    value: str


class DocstringExamplesSection(BaseModel):
    kind: Literal[DocstringSectionKind.EXAMPLES] = DocstringSectionKind.EXAMPLES
    items: tuple[DocstringExamplesSectionItem, ...]


class DocstringGyomuContextSection(BaseModel):
    kind: Literal[DocstringSectionKind.GYOMU_CONTEXT] = (
        DocstringSectionKind.GYOMU_CONTEXT
    )
    value: str


class DocstringCustomSection(BaseModel):
    kind: Literal[DocstringSectionKind.CUSTOM] = DocstringSectionKind.CUSTOM
    title: str
    value: str


class DocstringNotesSection(BaseModel):
    kind: Literal[DocstringSectionKind.NOTES] = DocstringSectionKind.NOTES
    value: str


type DocstringSection = (
    DocstringParametersSection
    | DocstringReturnsSection
    | DocstringRaisesSection
    | DocstringExamplesSection
    | DocstringNotesSection
    | DocstringGyomuContextSection
    | DocstringCustomSection
)


class DocstringAnalysis(BaseModel):
    raw: str
    summary: str | None
    description: str | None
    style: DocstringStyle
    location: SourceLocation
    sections: tuple[DocstringSection, ...]
    indent: int


class DocstringCommon(TypedDict):
    location: SourceLocation
    indent: int
