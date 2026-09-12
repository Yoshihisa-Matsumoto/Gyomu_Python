from pydantic import BaseModel


class PydanticFieldAnalysis(BaseModel):
    default_source: str | None
    description: str | None
    alias: str | None
    required: bool
