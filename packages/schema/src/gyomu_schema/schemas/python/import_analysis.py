from enum import StrEnum

from pydantic import BaseModel


class ImportKind(StrEnum):
    MODULE = "module"
    SYMBOL = "symbol"


class ImportAnalysis(BaseModel):
    local_name: str
    imported_name: str
    kind: ImportKind
