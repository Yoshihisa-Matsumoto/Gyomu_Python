from gyomu_schema.schemas.python.docstring import DocstringAnalysis
from gyomu_schema.schemas.python.import_analysis import ImportAnalysis
from gyomu_schema.schemas.python.symbol import SymbolAnalysis
from pydantic import BaseModel


class ModuleAnalysis(BaseModel):
    path: str
    name: str
    docstring: DocstringAnalysis | None
    imports: tuple[ImportAnalysis, ...]
    symbols: tuple[SymbolAnalysis, ...]
