from dataclasses import dataclass

from gyomu_schema.schemas.python.docstring import DocstringAnalysis
from gyomu_schema.schemas.python.types import DeclarationIdentity


@dataclass
class UpdatedDocstring:
    identity: DeclarationIdentity
    docstring: DocstringAnalysis
