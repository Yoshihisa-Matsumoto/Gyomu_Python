from typing import Literal, Self

from gyomu_schema.schemas.python.dependency import DependencySummary
from gyomu_schema.schemas.python.types import DeclarationIdentity
from pydantic import BaseModel


class DeclarationInfo(BaseModel):
    """Represents information about a declaration."""

    name: str
    """The name of the declaration."""

    kind: str
    """The kind of the declaration."""


class DocstringParameter(BaseModel):
    """Represents parameter documentation details within a docstring."""

    name: str
    """The name of the parameter."""

    sort_order: int
    """The sort order position of the parameter."""

    type: str | None
    """The type hint of the parameter."""

    description: str | None
    """The description of the parameter."""


class DocstringRaise(BaseModel):
    """Represents exception raise documentation details within a docstring."""

    type: str
    """The error type of the exception."""

    description: str
    """The description of the exception."""


class DocstringReturn(BaseModel):
    """Represents return value documentation details within a docstring."""

    type: str | None
    """The return type."""

    description: str
    """The description of the return value."""


class ExistingDocstring(BaseModel):
    """Represents the existing structured docstring of a declaration."""

    summary: str | None
    """The summary section of the docstring."""

    description: str | None
    """The detailed description section of the docstring."""

    parameters: tuple[DocstringParameter, ...]
    """The documented parameters."""

    returns: DocstringReturn | None
    """The documented return value."""

    raises: tuple[DocstringRaise, ...]
    """The documented raised exceptions."""


class DocumentableContext(BaseModel):
    """Indicates that a declaration context is documentable."""

    documentable: Literal[True] = True
    """Flag indicating whether the element is documentable."""


class NonDocumentableContext(BaseModel):
    """Indicates that a declaration context is non-documentable with a given reason."""

    reason: Literal["generated", "external", "non-documentable-member"]
    """The reason why the element is non-documentable."""

    documentable: Literal[False] = False
    """Flag indicating whether the element is documentable."""


class ContextEntry(BaseModel):
    """Context for generating a docstring for a Python declaration."""

    target: DeclarationIdentity
    """The declaration identity of the target."""

    member: DeclarationInfo
    """The member information."""

    existing_docstring: ExistingDocstring | None
    """The existing docstring information, if any."""

    children: tuple[Self, ...]
    """Child context entries."""

    documentable: DocumentableContext | NonDocumentableContext
    """Indicates whether the entry is documentable."""


class DocstringDeclarationContext(BaseModel):
    """Context for generating a docstring for a Python declaration."""

    target: DeclarationIdentity
    """The declaration identity of the target."""

    symbol: DeclarationInfo
    """The symbol information of the declaration."""

    code: str
    """The source code string of the declaration."""

    existing_docstring: ExistingDocstring | None
    """The existing docstring information, if available."""

    dependencies: tuple[DependencySummary, ...] | None
    """Summaries of dependencies referenced by the declaration."""

    children: tuple[ContextEntry, ...]
    """Child context entries representing nested members."""
