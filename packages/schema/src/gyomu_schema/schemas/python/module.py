from pydantic import BaseModel

from gyomu_schema.schemas.python.docstring import DocstringAnalysis
from gyomu_schema.schemas.python.import_analysis import ImportAnalysis
from gyomu_schema.schemas.python.symbol import SymbolAnalysis
from gyomu_schema.schemas.python.types import SourceRelativePath


class ModuleAnalysis(BaseModel):
    path: SourceRelativePath
    name: str
    docstring: DocstringAnalysis | None
    imports: tuple[ImportAnalysis, ...]
    symbols: tuple[SymbolAnalysis, ...]
