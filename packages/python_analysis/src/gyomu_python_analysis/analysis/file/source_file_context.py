from dataclasses import dataclass

from griffe import Module
from gyomu_schema.schemas.python.types import SourceRelativePath


@dataclass(frozen=True)
class SourceFileContext:
    """Represents the context of a source file, including its module representation
    and relative path.
    """

    module: Module
    """The parsed module representation."""

    path: SourceRelativePath
    """The source-relative path of the file."""
