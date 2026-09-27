from gyomu_schema.schemas.python.location import SourceLocation
from gyomu_schema.schemas.python.types import DeclarationIdentity
from pydantic import BaseModel


class FileUpdatePlanEntry(BaseModel):
    """Defines a planned update entry for a file.

    Represents a planned update entry for a specific declaration, including its
    identity, source location, and replacement text.
    """

    identity: DeclarationIdentity
    """The unique identity of the declaration being updated.

    The unique identity of the declaration being updated.
    """
    location: SourceLocation
    """The source location where the update should be applied.

    The source location where the update should be applied.
    """
    new_text: str
    """The new text to be written at the specified location.

    The new text to be written at the specified location.
    """


class FileUpdatePlan(BaseModel):
    """Defines a file update plan.

    Represents a complete file update plan containing a collection of file update plan
    entries.
    """

    items: tuple[FileUpdatePlanEntry, ...]
    """The update plan entries.

    A tuple of file update plan entries to be applied.
    """
