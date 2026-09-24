from enum import StrEnum

from pydantic import BaseModel


class TypeStructureKind(StrEnum):
    """Enumeration representing various kind categories of type structures."""

    NAME = "name"
    """Name type structure kind."""

    GENERIC = "generic"
    """Generic type structure kind."""

    UNION = "union"
    """Union type structure kind."""

    LITERAL = "literal"
    """Literal type structure kind."""

    CALLABLE = "callable"
    """Callable type structure kind."""

    NONE = "none"
    """None type structure kind."""

    UNKNOWN = "unknown"
    """Unknown type structure kind."""

    ATTRIBUTE = "attribute"
    """Attribute type structure kind."""

    TUPLE = "tuple"
    """Tuple type structure kind."""

    ARRAY = "array"
    """Array type structure kind."""

    DICTIONARY = "dictionary"
    """Dictionary type structure kind."""

    SET = "set"
    """Set type structure kind."""

    KEYWORD = "keyword"
    """Keyword type structure kind."""

    CALL = "call"
    """Call type structure kind."""

    ELLIPSIS = "ellipsis"
    """Ellipsis type structure kind."""


class NoneStructureAnalysis(BaseModel):
    """Defines a structure analysis for None types."""

    kind: TypeStructureKind = TypeStructureKind.NONE
    """The kind of the type structure."""


class NameStructureAnalysis(BaseModel):
    """Defines a structure analysis for named types containing a name identifier."""

    kind: TypeStructureKind = TypeStructureKind.NAME
    """The kind of the type structure."""

    name: str
    """The name identifier of the type."""


class UnknownStructureAnalysis(BaseModel):
    """Defines a structure analysis for unknown types."""

    kind: TypeStructureKind = TypeStructureKind.UNKNOWN
    """The kind of the type structure."""


class LiteralValue(BaseModel):
    """Defines a wrapper schema for literal values of various primitive types."""

    value: str | bytes | bool | int | float | complex
    """The underlying literal value."""


class EllipsisStructureAnalysis(BaseModel):
    """Defines a structure analysis for ellipsis types."""

    kind: TypeStructureKind = TypeStructureKind.ELLIPSIS
    """The kind of the type structure."""
