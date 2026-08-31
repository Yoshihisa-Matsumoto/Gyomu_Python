from enum import StrEnum

from gyomu_schema.schemas.python.location import SourceLocation
from pydantic import BaseModel


class DocstringParameter(BaseModel):
    name: str
    description: str


class DocstringReturns(BaseModel):
    description: str


class DocstringRaise(BaseModel):
    name: str
    description: str


class DocstringAnalysis(BaseModel):
    raw: str
    summary: str | None
    description: str | None
    location: SourceLocation
    parameters: tuple[DocstringParameter, ...]
    returns: DocstringReturns | None
    raises: tuple[DocstringRaise, ...]


class DocstringFormat(StrEnum):
    GOOGLE = "google"
