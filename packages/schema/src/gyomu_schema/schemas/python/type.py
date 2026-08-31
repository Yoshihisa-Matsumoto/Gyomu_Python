from enum import StrEnum

from pydantic import BaseModel


class TypeKind(StrEnum):
    NAME = "name"
    GENERIC = "generic"
    UNION = "union"
    LITERAL = "literal"
    CALLABLE = "callable"
    NONE = "none"
    UNKNOWN = "unknown"


class TypeAnalysis(BaseModel):
    kind: TypeKind
    name: str
