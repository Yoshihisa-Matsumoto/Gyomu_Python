from typing import Literal, Self

from gyomu_schema.schemas.python.dependency import DependencySummary
from gyomu_schema.schemas.python.types import DeclarationIdentity
from pydantic import BaseModel


class DeclarationInfo(BaseModel):
    name: str
    kind: str


class DocstringParameter(BaseModel):
    name: str
    sort_order: int
    type: str | None
    description: str | None


class DocstringRaise(BaseModel):
    type: str
    description: str


class DocstringReturn(BaseModel):
    type: str | None
    description: str


class ExistingDocstring(BaseModel):
    summary: str | None
    description: str | None
    parameters: tuple[DocstringParameter, ...]
    returns: DocstringReturn | None
    raises: tuple[DocstringRaise, ...]


class DocumentableContext(BaseModel):
    documentable: Literal[True] = True


class NonDocumentableContext(BaseModel):
    reason: Literal["generated", "external", "non-documentable-member"]
    documentable: Literal[False] = False


class ContextEntry(BaseModel):
    """Context for generating a docstring for a Python declaration."""

    target: DeclarationIdentity

    member: DeclarationInfo

    existing_docstring: ExistingDocstring | None

    children: tuple[Self, ...]

    documentable: DocumentableContext | NonDocumentableContext


class DocstringDeclarationContext(BaseModel):
    """Context for generating a docstring for a Python declaration."""

    target: DeclarationIdentity

    symbol: DeclarationInfo

    code: str

    existing_docstring: ExistingDocstring | None

    dependencies: tuple[DependencySummary, ...] | None

    children: tuple[ContextEntry, ...]
