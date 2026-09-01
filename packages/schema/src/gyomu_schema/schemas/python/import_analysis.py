from pydantic import BaseModel


class ImportAnalysis(BaseModel):
    local_name: str
    imported_name: str
