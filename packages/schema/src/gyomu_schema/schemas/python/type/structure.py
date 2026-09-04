from enum import StrEnum

from pydantic import BaseModel


class TypeStructureKind(StrEnum):
    NAME = "name"
    GENERIC = "generic"
    UNION = "union"
    LITERAL = "literal"
    CALLABLE = "callable"
    NONE = "none"
    UNKNOWN = "unknown"
    ATTRIBUTE = "attribute"
    TUPLE = "tuple"
    ARRAY = "array"
    DICTIONARY = "dictionary"
    SET = "set"


class NoneStructureAnalysis(BaseModel):
    kind: TypeStructureKind = TypeStructureKind.NONE


class NameStructureAnalysis(BaseModel):
    kind: TypeStructureKind = TypeStructureKind.NAME
    name: str


class UnknownStructureAnalysis(BaseModel):
    kind: TypeStructureKind = TypeStructureKind.UNKNOWN


class LiteralValue(BaseModel):
    value: str | int | bool
