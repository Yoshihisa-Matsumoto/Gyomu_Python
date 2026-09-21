from gyomu_schema.schemas.python.docstring import DocstringAnalysis
from gyomu_schema.schemas.python.types import DeclarationIdentity
from pydantic import BaseModel


class UpdatedDocstring(BaseModel):
    identity: DeclarationIdentity
    docstring: DocstringAnalysis
