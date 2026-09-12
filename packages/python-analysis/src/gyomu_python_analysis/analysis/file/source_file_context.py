from dataclasses import dataclass

from griffe import Module
from gyomu_schema.schemas.python.types import SourceRelativePath


@dataclass(frozen=True)
class SourceFileContext:
    module: Module
    path: SourceRelativePath
