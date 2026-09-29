from pydantic import BaseModel

from gyomu_schema.schemas.python.symbol_base import DeclarationKind
from gyomu_schema.schemas.python.types import ProjectRelativePath


class PublicDeclarationSummary(BaseModel):
    """Defines a summary of a public declaration, including its symbol name, declaration
    kind, and summary description.

    None
    """

    symbol: str
    """The name of the symbol.

    None
    """
    kind: DeclarationKind
    """The kind of declaration.

    None
    """
    summary: str
    """A summary description of the declaration.

    None
    """


class DependencySummary(BaseModel):
    """Defines a summary of a dependency, including its target and an external
    indicator.

    None
    """

    target: str
    """The target of the dependency.

    None
    """
    external: bool
    """Whether the dependency is external.

    None
    """


class FileSummary(BaseModel):
    """Defines a file summary containing its path, public exports, and dependencies.

    None
    """

    path: ProjectRelativePath
    """The project-relative path of the file.

    None
    """
    exports: tuple[PublicDeclarationSummary, ...]
    """The public declarations exported by the file.

    None
    """
    dependencies: tuple[DependencySummary, ...]
    """The dependencies required by the file.

    None
    """
