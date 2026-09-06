from pydantic import BaseModel

from gyomu_schema.schemas.python.location import SourceLocation
from gyomu_schema.schemas.python.type.type_analysis import TypeExpression


class DecoratorArgument(BaseModel):
    expression: TypeExpression
    name: str | None = None


class DecoratorAnalysis(BaseModel):
    name: str
    arguments: tuple[DecoratorArgument, ...]
    location: SourceLocation | None
