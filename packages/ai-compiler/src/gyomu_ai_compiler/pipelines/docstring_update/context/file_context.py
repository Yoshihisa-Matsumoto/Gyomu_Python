from dataclasses import dataclass

from gyomu_schema.schemas.python.types import (
    DeclarationIdentity,
    SourceRelativePath,
)

from gyomu_ai_compiler.pipelines.docstring_update.context.declaration_context import (
    DocstringDeclarationContext,
)


@dataclass(frozen=True)
class RetryOption:
    attempt: int
    missing_identity: tuple[DeclarationIdentity]


@dataclass(frozen=True)
class DocstringFileContext:
    project_name: str
    source_relative_path: SourceRelativePath
    symbols: tuple[DocstringDeclarationContext, ...]
    retry: RetryOption | None
