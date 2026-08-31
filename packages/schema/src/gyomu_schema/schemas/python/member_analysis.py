from enum import StrEnum

from gyomu_schema.schemas.python.decorator import DecoratorAnalysis
from gyomu_schema.schemas.python.docstring import DocstringAnalysis
from gyomu_schema.schemas.python.location import SourceLocation
from gyomu_schema.schemas.python.visibility import Visibility
from pydantic import BaseModel


class MemberKind(StrEnum):
    VARIABLE = "variable"
    METHOD = "method"


class MemberAnalysisBase(BaseModel):
    name: str
    visibility: Visibility
    location: SourceLocation
    docstring: DocstringAnalysis | None
    decorators: tuple[DecoratorAnalysis, ...]
