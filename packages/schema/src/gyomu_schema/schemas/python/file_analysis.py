from dataclasses import dataclass

from gyomu_schema.schemas.python.docstring import DocstringAnalysis
from gyomu_schema.schemas.python.module import ModuleAnalysis
from gyomu_schema.schemas.python.symbol import MemberAnalysis, SymbolAnalysis
from gyomu_schema.schemas.python.types import DeclarationIdentity


@dataclass()
class FileAnalysisMetadata:
    parsed_docstring: dict[DeclarationIdentity, DocstringAnalysis]
    symbols: dict[DeclarationIdentity, SymbolAnalysis | MemberAnalysis]


@dataclass()
class FileAnalysisContext:
    metadata: FileAnalysisMetadata
    analysis: ModuleAnalysis
