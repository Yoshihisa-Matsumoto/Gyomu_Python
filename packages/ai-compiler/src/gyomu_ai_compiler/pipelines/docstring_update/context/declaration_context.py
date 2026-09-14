from dataclasses import dataclass
from typing import Literal, Self

from gyomu_schema.schemas.python.dependency import DependencySummary
from gyomu_schema.schemas.python.types import DeclarationIdentity


@dataclass(frozen=True)
class DeclarationInfo:
    name: str
    kind: str


@dataclass(frozen=True)
class DocstringParameter:
    name: str
    sort_order: int
    type: str | None
    description: str | None


@dataclass(frozen=True)
class DocstringRaise:
    type: str
    description: str


@dataclass(frozen=True)
class DocstringReturn:
    type: str | None
    description: str


@dataclass(frozen=True)
class ExistingDocstring:
    summary: str | None
    description: str | None
    parameters: tuple[DocstringParameter, ...]
    returns: DocstringReturn | None
    raises: tuple[DocstringRaise, ...]


@dataclass(frozen=True)
class DocumentableContext:
    documentable: Literal[True] = True


@dataclass(frozen=True)
class NonDocumentableContext:
    reason: Literal["generated", "external", "non-documentable-member"]
    documentable: Literal[False] = False


@dataclass(frozen=True)
class ContextEntry:
    """Context for generating a docstring for a Python declaration."""

    target: DeclarationIdentity

    member: DeclarationInfo

    existing_docstring: ExistingDocstring | None

    children: tuple[Self, ...]

    documentable: DocumentableContext | NonDocumentableContext


@dataclass(frozen=True)
class DocstringDeclarationContext:
    """Context for generating a docstring for a Python declaration."""

    target: DeclarationIdentity

    symbol: DeclarationInfo

    code: str

    existing_docstring: ExistingDocstring | None

    dependencies: tuple[DependencySummary, ...] | None

    children: tuple[ContextEntry, ...]
