from dataclasses import dataclass

from gyomu_schema.schemas.python.docstring import DocstringAnalysis
from gyomu_schema.schemas.python.module import ModuleAnalysis
from gyomu_schema.schemas.python.types import SymbolId


@dataclass()
class FileAnalysisMetadata:
    parsed_docstring: dict[SymbolId, DocstringAnalysis]


@dataclass()
class FileAnalysisContext:
    metadata: FileAnalysisMetadata
    analysis: ModuleAnalysis
