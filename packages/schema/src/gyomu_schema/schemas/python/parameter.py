from enum import StrEnum

from gyomu_schema.schemas.python.type import TypeAnalysis
from pydantic import BaseModel


class ParameterKind(StrEnum):
    POSITIONAL_ONLY = "positional_only"
    POSITIONAL_OR_KEYWORD = "positional_or_keyword"
    VAR_POSITIONAL = "var_positional"
    KEYWORD_ONLY = "keyword_only"
    VAR_KEYWORD = "var_keyword"


class ParameterAnalysis(BaseModel):
    name: str
    kind: ParameterKind
    type: TypeAnalysis | None
    default: ...
