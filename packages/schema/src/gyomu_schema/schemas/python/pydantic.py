from gyomu_schema.schemas.python.type import TypeAnalysis
from pydantic import BaseModel


class PydanticFieldAnalysis(BaseModel):
    name: str
    type: TypeAnalysis | None
    default_source: str | None
    required: bool
    description: str | None
    alias: str | None


class PydanticModelAnalysis(BaseModel):
    fields: tuple[PydanticFieldAnalysis, ...]
