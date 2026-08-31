from gyomu_schema.schemas.python.location import SourceLocation
from pydantic import BaseModel


class DecoratorAnalysis(BaseModel):
    name: str
    arguments_source: tuple[str, ...]
    location: SourceLocation
