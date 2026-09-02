from pydantic import BaseModel

from gyomu_schema.schemas.python.type.type_analysis import TypeAnalysis


class PydanticFieldAnalysis(BaseModel):
    name: str
    type: TypeAnalysis | None
    default_source: str | None
    required: bool
    description: str | None
    alias: str | None


class PydanticModelAnalysis(BaseModel):
    fields: tuple[PydanticFieldAnalysis, ...]
