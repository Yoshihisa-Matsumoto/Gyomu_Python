from gyomu_schema.schemas.python.types import (
    DeclarationIdentity,
    SourceRelativePath,
)
from pydantic import BaseModel

from gyomu_ai_compiler.pipelines.docstring_update.context.declaration_context import (
    DocstringDeclarationContext,
)


class DocstringRetryOption(BaseModel):
    """Represents retry configuration options for docstring generation attempts."""

    attempt: int
    """The current retry attempt number."""

    missing_identity: tuple[DeclarationIdentity, ...]
    """A tuple of declaration identities that are missing documentation and need to
    be retried.
    """


class DocstringFileContext(BaseModel):
    """Represents the context for a file undergoing docstring updates, including its
    symbols and retry options.
    """

    project_name: str
    """The name of the project containing the file."""

    source_relative_path: SourceRelativePath
    """The relative path to the source file."""

    symbols: tuple[DocstringDeclarationContext, ...]
    """A tuple of declaration contexts within the file."""

    retry: DocstringRetryOption | None
    """Optional retry options for docstring generation."""
