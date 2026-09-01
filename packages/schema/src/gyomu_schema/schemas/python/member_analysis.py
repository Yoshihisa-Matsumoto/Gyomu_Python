from enum import StrEnum
from typing import TypedDict

from pydantic import BaseModel

from gyomu_schema.schemas.python.decorator import DecoratorAnalysis
from gyomu_schema.schemas.python.docstring import DocstringAnalysis
from gyomu_schema.schemas.python.location import SourceLocation
from gyomu_schema.schemas.python.visibility import Visibility


class MemberKind(StrEnum):
    VARIABLE = "variable"
    METHOD = "method"


class MemberAnalysisBase(BaseModel):
    name: str
    visibility: Visibility
    location: SourceLocation | None
    docstring: DocstringAnalysis | None
    decorators: tuple[DecoratorAnalysis, ...]
    indent: int | None


class MemberCommon(TypedDict):
    name: str
    location: SourceLocation | None
    visibility: Visibility
    indent: int | None
