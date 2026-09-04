from enum import StrEnum

from pydantic import BaseModel

from gyomu_schema.schemas.python.location import SourceLocation


class DocstringSectionKind(StrEnum):
    ARGS = "args"
    RETURNS = "returns"
    RAISES = "raises"
    EXAMPLES = "examples"
    NOTES = "notes"
    CUSTOM = "custom"
    GYOMU_CONTEXT = "gyomu_context"


class DocstringSection(BaseModel):
    kind: DocstringSectionKind
    name: str
    value: str


class DocstringStyle(StrEnum):
    GOOGLE = "google"


class DocstringAnalysis(BaseModel):
    raw: str
    style: DocstringStyle
    location: SourceLocation
    sections: tuple[DocstringSection, ...]
