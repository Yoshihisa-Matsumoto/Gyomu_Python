from gyomu_schema.schemas.python.docstring import DocstringAnalysis
from gyomu_schema.schemas.python.types import DeclarationIdentity
from pydantic import BaseModel


class UpdatedDocstring(BaseModel):
    """Represents an updated docstring for a specific declaration.

    Represents an updated docstring associated with a specific declaration identity.
    """

    identity: DeclarationIdentity
    """The declaration identity.

    The unique identity of the declaration being updated.
    """
    docstring: DocstringAnalysis
    """The docstring analysis.

    The docstring analysis containing the updated documentation content.
    """
