from dataclasses import dataclass

from gyomu_schema.schemas.python.docstring import DocstringAnalysis
from gyomu_schema.schemas.python.module import ModuleAnalysis
from gyomu_schema.schemas.python.symbol import MemberAnalysis, SymbolAnalysis
from gyomu_schema.schemas.python.types import DeclarationIdentity


@dataclass()
class FileAnalysisMetadata:
    """Represents metadata for a file analysis.

    Represents metadata for a file analysis containing parsed docstrings and symbol
    analyses.
    """

    parsed_docstring: dict[DeclarationIdentity, DocstringAnalysis]
    """Parsed docstring analyses by declaration identity.

    A dictionary mapping declaration identities to their parsed docstring analyses.
    """
    symbols: dict[DeclarationIdentity, SymbolAnalysis | MemberAnalysis]
    """Symbol and member analyses by declaration identity.

    A dictionary mapping declaration identities to their symbol or member analyses.
    """


@dataclass()
class FileAnalysisContext:
    """Represents the context for a file analysis.

    Represents the complete context for a file analysis, combining file metadata and
    module analysis.
    """

    metadata: FileAnalysisMetadata
    """File analysis metadata.

    Metadata associated with the file analysis.
    """
    analysis: ModuleAnalysis
    """Module analysis.

    Module analysis results for the file.
    """
