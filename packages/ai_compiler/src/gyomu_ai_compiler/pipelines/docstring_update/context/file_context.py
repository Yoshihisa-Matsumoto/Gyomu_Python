from gyomu_schema.schemas.python.types import (
    DeclarationIdentity,
    SourceRelativePath,
)
from pydantic import BaseModel

from gyomu_ai_compiler.pipelines.docstring_update.context.declaration_context import (
    DocstringDeclarationContext,
)


class DocstringRetryOption(BaseModel):
    attempt: int
    missing_identity: tuple[DeclarationIdentity, ...]


class DocstringFileContext(BaseModel):
    project_name: str
    source_relative_path: SourceRelativePath
    symbols: tuple[DocstringDeclarationContext, ...]
    retry: DocstringRetryOption | None
