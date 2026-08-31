from pydantic import BaseModel


class ImportAnalysis(BaseModel):
    module: str
    imported_name: str | None
    alias: str | None
    is_relative: bool
    relative_level: int
