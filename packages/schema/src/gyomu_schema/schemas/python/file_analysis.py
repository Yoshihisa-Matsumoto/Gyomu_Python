from dataclasses import dataclass

from gyomu_schema.schemas.python.docstring import DocstringAnalysis
from gyomu_schema.schemas.python.module import ModuleAnalysis


@dataclass()
class FileAnalysisMetadata:
    parsed_docstring: dict[str, DocstringAnalysis]


@dataclass()
class FileAnalysisContext:
    metadata: FileAnalysisMetadata
    analysis: ModuleAnalysis
